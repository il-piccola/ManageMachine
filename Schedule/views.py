import datetime
from django.shortcuts import render, redirect
from django_pandas.io import read_frame
from plotly import express
from plotly.offline import plot
from ManageMachine.models import *
from .forms import *

def show(request) :
    params = getTitleAndMsg()
    if (request.method != 'POST') :
        params['form'] = SearchForm(datetime=datetime.datetime.now())
        return render(request, 'Schedule/show.html', params)
    form = SearchForm(data=request.POST, datetime=datetime.datetime.now())
    if (form.is_valid()) :
        machine = form.cleaned_data['machine']
        date = form.cleaned_data['date']
        start = datetime.datetime.combine(date, form.cleaned_data['start'])
        end = datetime.datetime.combine(date, form.cleaned_data['end'])
        models = Schedule.objects.filter(machine=machine, start__gte=start, end__lt=end).order_by('start')
        params['models'] = models
        if (models.count() > 0) :
            params['fig'] = makeGanttChartHtml(models, start, end)
    params['form'] = form
    return render(request, 'Schedule/show.html', params)

def showFromOrder(request, order, name) :
    params = getTitleAndMsg()
    machine = getMachineId(name)
    schedules = Schedule.objects.filter(machine=machine, order=order)
    if (schedules.count() <= 0) :
        return redirect('Schedule:show')
    time = fromDawnTillDuskD(convertDateTimeAware(schedules.first().start))
    s = convertDateTimeNative(time[0])
    e = convertDateTimeNative(time[1])
    models = Schedule.objects.filter(machine=machine, start__gte=s, end__lt=e).order_by('start')
    params['models'] = models
    if (models.count() > 0) :
        params['fig'] = makeGanttChartHtml(models, time[0], time[1])
    params['form'] = SearchForm(initial={'machine':str(machine)}, datetime=time[0])
    return render(request, 'Schedule/show.html', params)

def getTitleAndMsg() :
    return {
        'title' : 'Show Machine Schedule',
        'msg' : '印刷機の予約状況を表示します',
    }

def makeGanttChartHtml(models, start, end) :
    # plotlyに渡すDataFrameを作成
    df = read_frame(models)
    df.drop(['id', 'machine'], axis=1, inplace=True)
    df.rename(columns={'order':PLOTLY_COL_NAME[0], 'start':PLOTLY_COL_NAME[1], 'end':PLOTLY_COL_NAME[2]}, inplace=True)
    print(df)
    # plotlyを使用してHTMLを生成
    fig = express.timeline(
        df,
        x_start=PLOTLY_COL_NAME[1],
        x_end=PLOTLY_COL_NAME[2], 
        y=PLOTLY_COL_NAME[0], 
        color=PLOTLY_COL_NAME[0],
        height=(len(df)*15+150),
        range_x=[start, end])
    fig.update_xaxes(tickformat="%H:%M")
    return plot(fig, output_type='div', include_plotlyjs=False)
