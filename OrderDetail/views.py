import datetime
import math
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from plotly import express
from plotly.offline import plot
from ManageMachine.settings import *
from ManageMachine.models import *
from .forms import *
from django_pandas.io import read_frame

def show(request, order) :
    df = getDetail(order)
    fig = makeGanttChartHtml(df)
    initial = getAutoScheduleInitial(order, df)
    params = {
        'title' : 'Order Detail',
        'msg' : CSV_COL_NAME[0] + '【' + order + '】の詳細を表示します',
        'order' : order,
        'df' : df,
        'fig' : fig,
    }
    if (request.method == 'POST' and 'btn_auto' in request.POST) :
        saveScheduleAuto(request, params, order, df)
        params['formset'] = makeScheduleFormSet(order)
    elif (request.method == 'POST' and 'btn_manual' in request.POST) :
        saveScheduleManual(request, params, order)
        params['autoform'] = AutoScheduleForm(initial=initial)
    else :
        params['autoform'] = AutoScheduleForm(initial=initial)
        params['formset'] = makeScheduleFormSet(order)
    return render(request, 'OrderDetail/show.html', params)

def getDetail(number) :
    df = readCsv()
    if not df.empty :
        df = df[df[CSV_COL_NAME[0]] == number]
        df.sort_values(CSV_COL_NAME[2], inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df

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

def getScheduleTime(machine, start, minutes) :
    ret = getStartTimeOfDate(start)
    while True :
        end = ret + minutes
        time = fromDawnTillDuskD(ret)
        if (end > time[1]) :
            ret = getStartTimeOfDate(end)
            end = ret + minutes
        schedules = getSchedulesInTerm(machine, ret, end)
        print('ret:', ret, 'end:', end)
        if (schedules.count() <= 0) :
            break
        ret = convertDateTimeAware(schedules.order_by('end').last().end)
    return ret

def getStartTimeOfDate(date) :
    ret = date
    machinetimes = MachineTime.objects.filter(weekday=ret.weekday())
    if (machinetimes.count() <= 0) :
        while (machinetimes.count() <= 0) :
            ret = getNextDay(ret)
            machinetimes = MachineTime.objects.filter(weekday=ret.weekday())
        ret = fromDawnTillDuskD(ret)[0]
    elif (ret > fromDawnTillDuskD(ret)[1]) :
        ret = getNextDay(ret)
        ret = getStartTimeOfDate(ret)
    elif (ret < fromDawnTillDuskD(ret)[0]) :
        ret = fromDawnTillDuskD(ret)[0]
    return ret

def getSchedulesInTerm(machine, start, end) :
    s = convertDateTimeNative(start)
    e = convertDateTimeNative(end)
    q1 = Q()
    q1.add(Q(machine=machine), Q.AND)
    q1.add(Q(start__lte=s), Q.AND)
    q1.add(Q(end__gt=s), Q.AND)
    q2 = Q()
    q2.add(Q(machine=machine), Q.AND)
    q2.add(Q(start__lt=e), Q.AND)
    q2.add(Q(end__gte=e), Q.AND)
    q3 = Q()
    q3.add(Q(machine=machine), Q.AND)
    q3.add(Q(start__gte=s), Q.AND)
    q3.add(Q(end__lte=e), Q.AND)
    schedules1 = Schedule.objects.filter(q1)
    schedules2 = Schedule.objects.filter(q2)
    schedules3 = Schedule.objects.filter(q3)
    print('machine:', Machine.objects.get(id=machine).name, 'start:', s, 'end:', e)
    print('schedules1')
    print(read_frame(schedules1))
    print('schedules2')
    print(read_frame(schedules2))
    print('schedules3')
    print(read_frame(schedules3))
    return (schedules1|schedules2|schedules3)

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
