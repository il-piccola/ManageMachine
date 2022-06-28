from django.urls import path
from . import views

app_name = 'Schedule'
urlpatterns = [
    path('show', views.show, name='show'),
    path('showFromOrder/<order>/<name>', views.showFromOrder, name='showFromOrder'),
    path('showFromTerm/<start>/<end>', views.showFromTerm, name='showFromTerm'),
]
