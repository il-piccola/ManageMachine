from django.urls import path
from . import views

app_name = 'Schedule'
urlpatterns = [
    path('show', views.show, name='show'),
]
