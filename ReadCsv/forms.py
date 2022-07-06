from django import forms
from ManageMachine.settings import *
from ManageMachine.models import *
from ManageMachine.utils import *

class UploadForm(forms.ModelForm) :
    class Meta :
        model = Csv
        fields = ['csv']

class SearchForm(forms.Form) :
    def getMachineMenu() :
        l = []
        l.append(('all', '全て'))
        for machine in Machine.objects.all() :
            l.append((str(machine.id), machine.name))
        return l
    def getSortMenu() :
        l = []
        l.append(('none', 'なし'))
        for i in range(len(CSV_COL_NAME)) :
            l.append((str(i), CSV_COL_NAME[i]))
        return l
    search = forms.CharField(label='検索', required=False, widget=forms.TextInput())
    machine = forms.ChoiceField(
        label=CSV_COL_NAME[1],
        choices=getMachineMenu(),
        widget=forms.Select())
    order = forms.ChoiceField(
        label='ソート',
        choices=getSortMenu(),
        widget=forms.Select())
    reverse = forms.ChoiceField(
        label='', 
        choices=(('False', '降順'), ('True', '昇順')),
        widget=forms.Select())

class confirmForm(forms.Form) :
    orders = forms.CharField(widget=forms.HiddenInput())
