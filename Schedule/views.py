import datetime
from django.shortcuts import render, redirect
from django_pandas.io import read_frame
from plotly import express
from plotly.offline import plot
from ManageMachine.models import *
from .forms import *

def getTitleAndMsg() :
    return {
        'title' : 'Show Machine Schedule',
        'msg' : '印刷機の予約状況を表示します',
    }

class MachineSchedule() :
    machine = None
    start = None
    end = None
    models = None
    fig = None
    def __init__(self, machine, start, end) :
        self.machine = Machine.objects.get(id=int(machine))
        self.start = convertDateTimeNative(start)
        self.end = convertDateTimeNative(end)
        self.models = Schedule.objects.filter(machine=self.machine.id, start__gte=self.start, end__lt=self.end).order_by('start')
        if (self.models.count() > 0) :
            self.fig = self.makeGanttChartHtml()
    def isModelExists(self) :
        if (self.models.count() > 0) :
            return True
        return False
    def getMachineName(self) :
        return self.machine.name
    def makeGanttChartHtml(self) :
        # plotlyに渡すDataFrameを作成
        df = read_frame(self.models)
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
            range_x=[self.start, self.end])
        fig.update_xaxes(tickformat="%H:%M")
        return plot(fig, output_type='div', include_plotlyjs=False)

def show(request) :
    params = getTitleAndMsg()
    if (request.method != 'POST') :
        params['form'] = SearchForm(datetime=datetime.datetime.now())
        return render(request, 'Schedule/show.html', params)
    form = SearchForm(data=request.POST, datetime=datetime.datetime.now())
    if (form.is_valid()) :
        machines = form.cleaned_data['machines']
        date = form.cleaned_data['date']
        start = datetime.datetime.combine(date, form.cleaned_data['start'])
        end = datetime.datetime.combine(date, form.cleaned_data['end'])
        machineScheduleList = []
        for machine in machines :
            machineScheduleList.append(MachineSchedule(machine, start, end))
        params['schedules'] = machineScheduleList
    params['form'] = form
    return render(request, 'Schedule/show.html', params)

def showFromOrder(request, order, name) :
    params = getTitleAndMsg()
    machine = getMachineId(name)
    schedules = Schedule.objects.filter(machine=machine, order=order)
    if (schedules.count() <= 0) :
        return redirect('Schedule:show')
    time = fromDawnTillDuskD(convertDateTimeAware(schedules.first().start))
    params['schedules'] = [MachineSchedule(str(machine), time[0], time[1])]
    params['form'] = SearchForm(initial={'machines':[str(machine)]}, datetime=time[0])
    return render(request, 'Schedule/show.html', params)
