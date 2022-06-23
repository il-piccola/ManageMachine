import datetime
from email.policy import default
from typing import Iterable
from django import forms
from ManageMachine.settings import *
from ManageMachine.models import *

class SearchForm(forms.Form) :
    def getMachineMenu() :
        l = []
        for machine in Machine.objects.all() :
            l.append((str(machine.id), machine.name))
        return l
    machine = forms.ChoiceField(
        label=CSV_COL_NAME[1],
        choices=getMachineMenu(),
        widget=forms.Select())
    date = forms.DateField(
        label='日付',
        widget=forms.DateInput(attrs={"type":"date"})
    )
    start = forms.TimeField(
        label='',
        widget=forms.TimeInput(attrs={"type":"time"})
    )
    end = forms.TimeField(
        label='',
        widget=forms.TimeInput(attrs={"type":"time"})
    )
    def __init__(self, *args, **kwargs) :
        super(SearchForm, self).__init__(*args, **kwargs)
        date = datetime.date.today()
        time = fromDawnTillDuskD(date)
        self.initial['date'] = date.strftime("%Y-%m-%d")
        self.initial['start'] = time[0].strftime("%H:%M")
        self.initial['end'] = time[1].strftime("%H:%M")
