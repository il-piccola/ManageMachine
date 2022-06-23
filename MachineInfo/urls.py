from django.urls import path
from . import views

app_name = 'MachineInfo'
urlpatterns = [
    path('show', views.show, name='show'),
]
