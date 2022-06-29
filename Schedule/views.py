import datetime
from django.shortcuts import render, redirect
from django_pandas.io import read_frame
from plotly import express
from plotly.offline import plot
from ManageMachine.models import *
from ManageMachine.utils import *
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
        # fig.update_xaxes(tickformat="%H:%M")
        return plot(fig, output_type='div', include_plotlyjs=False)

def show(request) :
    params = getTitleAndMsg()
    machines = []
    time = fromDawnTillDuskD(convertDateTimeAware(datetime.datetime.now()))
    start = time[0]
    end = time[1]
    if (request.method == 'POST' and 'btn_delete' in request.POST) :
        Schedule.objects.all().delete()
        return redirect('Schedule:show')
    elif (request.method != 'POST') :
        for machine in Machine.objects.all() :
            machines.append(str(machine.id))
        initial = {
            'machines' : machines,
            'start' : datetime.datetime.strftime(start, "%Y-%m-%dT%H:%M"),
            'end' : datetime.datetime.strftime(end, "%Y-%m-%dT%H:%M")
        }
        params['form'] = SearchForm(initial=initial)
    else :
        form = SearchForm(data=request.POST)
        if (form.is_valid()) :
            machines = form.cleaned_data['machines']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
        params['form'] = form
    machineScheduleList = []
    for machine in machines :
        machineScheduleList.append(MachineSchedule(machine, start, end))
    params['schedules'] = machineScheduleList
    return render(request, 'Schedule/show.html', params)

def showFromOrder(request, order, name) :
    params = getTitleAndMsg()
    machine = getMachineId(name)
    schedules = Schedule.objects.filter(machine=machine, order=order)
    if (schedules.count() <= 0) :
        return redirect('Schedule:show')
    time = fromDawnTillDuskD(convertDateTimeAware(schedules.first().start))
    params['schedules'] = [MachineSchedule(str(machine), time[0], time[1])]
    initial = {
        'machines' : [str(machine)],
        'start' : datetime.datetime.strftime(time[0], "%Y-%m-%dT%H:%M"),
        'end' : datetime.datetime.strftime(time[1], "%Y-%m-%dT%H:%M")
    }
    params['form'] = SearchForm(initial=initial)
    return render(request, 'Schedule/show.html', params)

def showFromTerm(request, start, end) :
    params = getTitleAndMsg()
    s = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M")
    e = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M")
    machines = []
    for machine in Machine.objects.all() :
        machines.append(str(machine.id))
    initial = {
        'machines' : machines,
        'start' : start,
        'end' : end
    }
    params['form'] = SearchForm(initial=initial)
    machineScheduleList = []
    for machine in machines :
        machineScheduleList.append(MachineSchedule(machine, s, e))
    params['schedules'] = machineScheduleList
    return render(request, 'Schedule/show.html', params)
