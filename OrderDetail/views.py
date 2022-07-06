import datetime
import math
import numpy as np
import pandas as pd
from django.shortcuts import render
from plotly import express
from plotly.offline import plot
from ManageMachine.settings import *
from ManageMachine.models import *
from ManageMachine.utils import *
from .forms import *

def show(request, order) :
    df = getDetail(order)
    fig = makeGanttChartHtml(df)
    initial = getAutoScheduleInitial(order, df)
    params = {
        'title' : 'Order Detail',
        'msg' : CSV_COL_NAME[0] + '【' + order + '】の詳細を表示します',
        'order' : order,
        'df' : df,
        'term' : getTerm(df),
        'fig' : fig,
    }
    if (request.method == 'POST' and 'btn_auto' in request.POST) :
        msg = isRegistingOrderList()
        if (len(msg) > 0) :
            params['msg'] = msg
        else :
            saveScheduleAuto(request, params, order, df)
            params['formset'] = makeScheduleFormSet(order)
            params['df'] = getDetail(order)
    elif (request.method == 'POST' and 'btn_manual' in request.POST) :
        msg = isRegistingOrderList()
        if (len(msg) > 0) :
            params['msg'] = msg
        else :
            saveScheduleManual(request, params, order)
            params['autoform'] = AutoScheduleForm(initial=initial)
            params['df'] = getDetail(order)
    else :
        params['autoform'] = AutoScheduleForm(initial=initial)
        params['formset'] = makeScheduleFormSet(order)
    return render(request, 'OrderDetail/show.html', params)

def getDetail(order) :
    df = readCsv()
    if not df.empty :
        df = df[df[CSV_COL_NAME[0]] == order]
        df.sort_values(CSV_COL_NAME[2], inplace=True)
        df.reset_index(drop=True, inplace=True)
        flg = []
        for index, row in df.iterrows() :
            machine = getMachineId(row[CSV_COL_NAME[1]])
            flg.append(Schedule.objects.filter(order=order, machine=machine).exists())
        df['flg'] = flg
    return df

def getTerm(df) :
    hours, minutes = convertHMFromMinutes(df[CSV_COL_NAME[4]].sum())
    ret = getTermStr(hours, minutes)
    ret = ret + "("
    for index, row in df.iterrows() :
        hours, minutes = convertHMFromMinutes(row[CSV_COL_NAME[4]])
        ret = ret + row[CSV_COL_NAME[1]] + "：" + getTermStr(hours, minutes)
        if (index < len(df)-1) :
            ret = ret + ","
    ret = ret + ")"
    return ret

def makeGanttChartHtml(df) :
    # 号機名に対応する序数列を追加しソート
    df1 = df.copy()
    df1[ORDER_COL_NAME] = df1[CSV_COL_NAME[1]].apply(lambda x: getMachineId(x) if isMachineExists(x) else -1)
    df1 = df1.sort_values([ORDER_COL_NAME, CSV_COL_NAME[1], CSV_COL_NAME[2]]).reset_index(drop=True)
    # 正味作業時間と付帯作業時間を別レコードに分割
    df2 = df1.drop(CSV_COL_NAME[3], axis=1).rename(columns={CSV_COL_NAME[2]: TIME_COL_NAME})
    df2[PLOTLY_COL_NAME[0]] = df2[CSV_COL_NAME[1]] + ' ' + CSV_COL_NAME[2]
    df3 = df1.drop(CSV_COL_NAME[2], axis=1).rename(columns={CSV_COL_NAME[3]: TIME_COL_NAME})
    df3[PLOTLY_COL_NAME[0]] = df3[CSV_COL_NAME[1]] + ' ' + CSV_COL_NAME[3]
    df4 = pd.concat([df2, df3]).sort_values(ORDER_COL_NAME).reset_index(drop=True)
    # plotlyに渡すDataFrameを作成
    idx = df4.columns.get_loc(TIME_COL_NAME)
    start = []
    finish = []
    for i in range(len(df4)) :
        if (i == 0) :
            start.append(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        else :
            start.append(finish[i-1])
        td = datetime.timedelta(minutes=math.ceil(df4.iat[i, idx]))
        finish.append(start[i] + td)
    df4[PLOTLY_COL_NAME[1]] = start
    df4[PLOTLY_COL_NAME[2]] = finish
    # plotlyを使用してHTMLを生成
    fig = express.timeline(
        df4, 
        x_start=PLOTLY_COL_NAME[1], 
        x_end=PLOTLY_COL_NAME[2], 
        y=PLOTLY_COL_NAME[0], 
        color=CSV_COL_NAME[1],
        height=(len(df4)*50+150))
    fig.update_yaxes(autorange='reversed')
    fig.update_xaxes(tickformat="%H:%M")
    return plot(fig, output_type='div', include_plotlyjs=False)

def getAutoScheduleInitial(order, df) :
    initial = {
        'order' : order,
        'machines' : ','.join(map(str, getMachineIdList(df[CSV_COL_NAME[1]]))),
        'minutes' : ','.join(map(str, list(map(int, list(map(np.ceil, df[CSV_COL_NAME[4]])))))),
    }
    return initial

def makeScheduleFormSet(order) :
    return ScheduleFormSet(queryset=Schedule.objects.filter(order=order))

def saveScheduleAuto(request, params, order, df) :
    autoform = AutoScheduleForm(data=request.POST)
    if (autoform.is_valid()) :
        Schedule.objects.filter(order=order).delete()
        start = convertDateTimeAware(autoform.cleaned_data['start'])
        for index, row in df.iterrows() :
            machine = getMachineId(row[CSV_COL_NAME[1]])
            minutes = datetime.timedelta(minutes=np.ceil(row[CSV_COL_NAME[4]]))
            s = getScheduleTime(machine, start, minutes)
            e = s + minutes
            Schedule.objects.create(
                machine=Machine.objects.get(id=machine), 
                order=order, 
                branch=0, 
                start=convertDateTimeNative(s), 
                end=convertDateTimeNative(e)
            )
            start = e + datetime.timedelta(hours=1)     # 次の機械の予約は最低1時間後
        resetBranch(order)
        params['msg'] = '印刷機の自動予約が成功しました'
    else :
        params['msg'] = '自動予約の情報入力に誤りがあります'
    params['autoform'] = autoform

def saveScheduleManual(request, params, order) :
    formset = ScheduleFormSet(request.POST or None)
    if (formset.is_valid()) :
        models = formset.save(commit=False)
        for obj in formset.deleted_objects :
            obj.delete()
        for model in models :
            model.order = order
            model.save()
        resetBranch(order)
        params['msg'] = 'スケジュールの手動修正を行いました'
        params['formset'] = makeScheduleFormSet(order)
    else :
        params['msg'] = '手動修正の情報入力に誤りがあります'
        params['formset'] = formset
