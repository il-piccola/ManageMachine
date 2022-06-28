import datetime
from email.policy import default
from turtle import filling
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
    machines = forms.MultipleChoiceField(
        label=CSV_COL_NAME[1],
        choices=getMachineMenu(),
        widget=forms.CheckboxSelectMultiple())
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
    def __init__(self, datetime, *args, **kwargs) :
        super(SearchForm, self).__init__(*args, **kwargs)
        time = fromDawnTillDuskD(datetime)
        self.initial['date'] = time[0].strftime("%Y-%m-%d")
        self.initial['start'] = time[0].strftime("%H:%M")
        self.initial['end'] = time[1].strftime("%H:%M")
