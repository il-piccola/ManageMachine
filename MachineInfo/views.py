from django.shortcuts import render
from ManageMachine.models import MachineTime
from .forms import *

def show(request) :
    models = MachineTime.objects.all()
    params = {
        'title' : 'Show Machine Info',
        'msg' : '印刷機の稼働時間を表示します',
        'models' : models,
        'form' : SearchForm(),
    }
    if (request.method != 'POST') :
        return render(request, 'MachineInfo/show.html', params)
    if str.isdecimal(request.POST['machine']) :
        machine = int(request.POST['machine'])
        models = models.filter(machine=machine)
    if str.isdecimal(request.POST['weekday']) :
        weekday = int(request.POST['weekday'])
        models = models.filter(weekday=weekday)
    form = SearchForm(data=request.POST)
    params['models'] = models
    params['form'] = form
    return render(request, 'MachineInfo/show.html', params)
