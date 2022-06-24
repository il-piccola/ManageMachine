import datetime
from unicodedata import decimal
from django import forms
from ManageMachine.settings import *
from ManageMachine.models import *

class AutoScheduleForm(forms.Form) :
    order = forms.CharField(
        widget=forms.HiddenInput(),
    )
    machines = forms.CharField(
        widget=forms.HiddenInput(),
    )
    minutes = forms.CharField(
        widget=forms.HiddenInput(),
    )
    start = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type":"datetime-local"}),
    )
    end = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type":"datetime-local"}),
    )
    def clean_end(self) :
        minutes = datetime.timedelta(minutes=sum(map(int, self.cleaned_data['minutes'].split(','))))
        end = self.cleaned_data['end']
        start = self.cleaned_data['start']
        if (end < start) :
            raise forms.ValidationError('終了日時に開始日時より前の日時は指定できません。')
        if (end - start < minutes) :
            raise forms.ValidationError('指定された期間が短すぎます。')
        return end

class ScheduleForm(forms.ModelForm) :
    class Meta :
        model = Schedule
        fields = ('id', 'machine', 'order', 'branch', 'start', 'end')
        widgets = {
            'id' : forms.HiddenInput(),
            'machine' : forms.Select(),
            'order' : forms.HiddenInput(),
            'branch' : forms.HiddenInput(),
            'start' : forms.DateTimeInput(attrs={"type":"datetime-local"}),
            'end' : forms.DateTimeInput(attrs={"type":"datetime-local"}),
        }
    def __init__(self, *args, **kwargs) :
        super(ScheduleForm, self).__init__(*args, **kwargs)
        if self.instance.start :    # datetime-localに値を表示させるための書式変換
            self.initial['start'] = self.instance.start.strftime("%Y-%m-%dT%H:%M")
            self.initial['end'] = self.instance.end.strftime("%Y-%m-%dT%H:%M")
    def clean_start(self) :
        machine = self.cleaned_data['machine']
        order = self.cleaned_data['order']
        branch = self.cleaned_data['branch']
        start = self.cleaned_data['start']
        if (isReservedDate(machine, order, branch, start)) :
            raise forms.ValidationError('別の予約が入っています。')
        return start
    def clean_end(self) :
        machine = self.cleaned_data['machine']
        order = self.cleaned_data['order']
        branch = self.cleaned_data['branch']
        end = self.cleaned_data['end']
        if ('start' in self.cleaned_data.keys()) :
            start = self.cleaned_data['start']
            if (end < start) :
                raise forms.ValidationError('終了日時に開始日時より前の日時は指定できません。')
        if (isReservedDate(machine, order, branch, end)) :
            raise forms.ValidationError('別の予約が入っています。')
        return end

ScheduleFormSet = forms.modelformset_factory(Schedule, form=ScheduleForm, extra=1, can_delete=True)
