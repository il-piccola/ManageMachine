from django import forms
from ManageMachine.settings import *
from ManageMachine.models import *

class SearchForm(forms.Form) :
    def getMachineMenu() :
        l = []
        l.append(('all', '全て'))
        for machine in Machine.objects.all() :
            l.append((str(machine.id), machine.name))
        return l
    def getWeekdayMenu() :
        l = []
        l.append(('all', '全て'))
        for i, name in enumerate(WEEKDAY_NAME) :
            l.append((str(i), name))
        return l
    machine = forms.ChoiceField(
        label=CSV_COL_NAME[1],
        choices=getMachineMenu(),
        widget=forms.Select())
    weekday = forms.ChoiceField(
        label='曜日',
        choices=getWeekdayMenu(),
        widget=forms.Select())
