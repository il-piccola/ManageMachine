from django.shortcuts import render, redirect
from ManageMachine.settings import *
from ManageMachine.models import *
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
    }
    if (request.method != 'POST') :
        return render(request, 'ReadCsv/show.html', params)
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
    form = SearchForm(data=request.POST)
    params['df'] = df
    params['form'] = form
    return render(request, 'ReadCsv/show.html', params)
