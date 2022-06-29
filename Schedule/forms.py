from django import forms
from ManageMachine.settings import *
from ManageMachine.models import *
from ManageMachine.utils import *

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
    start = forms.DateTimeField(
        label='',
        widget=forms.DateTimeInput(attrs={"type":"datetime-local"})
    )
    end = forms.DateTimeField(
        label='',
        widget=forms.DateTimeInput(attrs={"type":"datetime-local"})
    )
    def clean_end(self) :
        end = self.cleaned_data['end']
        start = self.cleaned_data['start']
        if (end < start) :
            raise forms.ValidationError('終了日時に開始日時より前の日時は指定できません。')
        return end
