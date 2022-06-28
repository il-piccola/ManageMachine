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
    start = forms.TimeField(
        label='',
        widget=forms.DateTimeInput(attrs={"type":"datetime-local"})
    )
    end = forms.TimeField(
        label='',
        widget=forms.DateTimeInput(attrs={"type":"datetime-local"})
    )
