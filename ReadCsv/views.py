import numpy as np
from zoneinfo import ZoneInfo
from django.shortcuts import render, redirect
from ManageMachine.settings import *
from ManageMachine.models import *
from ManageMachine.utils import *
from .forms import *

def upload(request) :
    params = {
        'title' : 'Upload CSV',
        'msg' : '工程予測結果CSVファイルをアップロードします',
        'form' : UploadForm(),
    }
    if (request.method == 'POST') :
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid() :
            path = saveCsv(form)
            if path :
                return redirect('ReadCsv:show')
            else :
                params['msg'] = 'CSVファイルのアップロードに失敗しました'
        else :
            params['msg'] = 'CSVファイル以外はアップロードできません'
    return render(request, 'ReadCsv/upload.html', params)

def show(request) :
    df = readCsv()
    if df.empty :
        return redirect('ReadCsv:upload')
    params = {
        'title' : 'Show CSV',
        'msg' : 'アップロードされたCSVファイルを表示します',
        'df' : df,
        'form' : SearchForm(),
        'registing' : False,
    }
    if (request.method != 'POST') :
        return render(request, 'ReadCsv/show.html', params)
    if ('btn_regist' in request.POST) :
        return confirm(request, params)
    params['df'] = makeDataFrame(request, df)
    params['form'] = SearchForm(data=request.POST)
    return render(request, 'ReadCsv/show.html', params)

def makeDataFrame(request, df) :
    if len(request.POST['search']) > 0 :
        queryStr = CSV_COL_NAME[0] + '.str.contains("' + request.POST['search'] + '")'
        df = df.query(queryStr, engine='python')
    if str.isdecimal(request.POST['machine']) :
        id = int(request.POST['machine'])
        df = df[df[CSV_COL_NAME[1]] == Machine.objects.get(id=id).name]
    if str.isdecimal(request.POST['order']) :
        order = int(request.POST['order'])
        ascending = True
        if request.POST['reverse'] == 'False' :
            ascending = False
        df.sort_values(CSV_COL_NAME[order], ascending=ascending, inplace=True)
    return df

def confirm(request, params) :
    msg = isRegistingOrderList()
    if (len(msg) > 0) :
        params['msg'] = msg
        params['registing'] = True
        return render(request, 'ReadCsv/show.html', params)
    checklist = request.POST.getlist('check')
    if (len(checklist) <= 0) :
        params['msg'] = '一括予約対象を選択してください'
        return render(request, 'ReadCsv/show.html', params)
    if (len(checklist) > 100) :
        params['msg'] = '一度に100件を超える一括予約はできません'
        return render(request, 'ReadCsv/show.html', params)
    checklist = list(map(int, checklist))
    print('checklist:', len(checklist), 'df:', len(params['df']))
    print('checklist:', checklist)
    df = readCsv().iloc[checklist, :]
    orderlist = list(df[CSV_COL_NAME[0]].drop_duplicates())
    initial = {'orders' : ','.join(orderlist)}
    params = {
        'title' : 'Regist Orders',
        'msg' : str(len(orderlist)) + '件の一括予約を実行します、時間がかかりますがよろしいですか？',
        'form' : confirmForm(initial=initial),
        'orderlist' : orderlist,
    }
    return render(request, 'ReadCsv/confirm.html', params)

def regist(request, params) :
    checklist = request.POST.getlist('check')
    if (len(checklist) <= 0) :
        return render(request, 'ReadCsv/show.html', params)
    if (len(checklist) > 100) :
        params['msg'] = '一度に100件を超える一括予約はできません'
        return render(request, 'ReadCsv/show.html', params)
    checklist = list(map(int, checklist))
    print('checklist:', len(checklist), 'df:', len(params['df']))
    print('checklist:', checklist)
    df = readCsv().iloc[checklist, :]
    df.sort_values(CSV_COL_NAME[4], ascending=False, inplace=True)
    orderlist = list(df[CSV_COL_NAME[0]].drop_duplicates())
    print(orderlist)
    df = readCsv()
    df = df[df[CSV_COL_NAME[0]].isin(orderlist)]
    start = datetime.datetime(2200, 12, 31, 23, 59, 59, tzinfo=ZoneInfo('Asia/Tokyo'))
    end = datetime.datetime(1900, 1, 1, 0, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo'))
    for order in orderlist :
        time = registScheduleFromOrder(getDetail(order, df))
        if (time[0] and start > time[0]) :
            start = time[0]
        if (time[1] and end < time[1]) :
            end = time[1]
    s = datetime.datetime.strftime(start, "%Y-%m-%dT%H:%M")
    e = datetime.datetime.strftime(end, "%Y-%m-%dT%H:%M")
    return redirect('Schedule:showFromTerm', s, e)

def getDetail(order, df) :
    ret = df.copy()
    ret = ret[ret[CSV_COL_NAME[0]] == order]
    ret.sort_values(CSV_COL_NAME[2], inplace=True)
    ret.reset_index(drop=True, inplace=True)
    return ret

def registScheduleFromOrder(df) :
    order = list(df[CSV_COL_NAME[0]])[0]
    Schedule.objects.filter(order=order).delete()
    start = datetime.datetime.now(tz=ZoneInfo('Asia/Tokyo'))
    ret = [None, None]
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
        if (index == 0) :
            ret[0] = s
        elif (index == len(df)-1) :
            ret[1] = e
        start = e + datetime.timedelta(hours=1)     # 次の機械の予約は最低1時間後
    return ret
