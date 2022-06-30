from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt
from ManageMachine.settings import *
from ManageMachine.models import *
from .forms import *

def index(request) :
    params = {
        'sitename' : SITE_NAME,
        'form' : LoginForm()
    }
    if (request.method != 'POST') :
        return render(request, 'MainMenu/index.html', params)
    form = LoginForm(data=request.POST)
    if (not form.is_valid()) :
        params['form'] = form
        return render(request, 'MainMenu/index.html', params)
    return redirect('MainMenu:index2')

@xframe_options_exempt  # インラインフレームを許可
def index2(request) :
    params = {
        'sitename' : SITE_NAME
    }
    return render(request, 'MainMenu/index2.html', params)

def menu(request) :
    params = {
        'sitename' : SITE_NAME
    }
    return render(request, 'MainMenu/menu.html', params)
