from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from ManageMachine.settings import *

def index(request) :
    params = {
        'sitename' : SITE_NAME
    }
    return render(request, 'MainMenu/index.html', params)

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
