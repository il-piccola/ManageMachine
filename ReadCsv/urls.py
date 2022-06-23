from django.urls import path
from . import views

app_name = 'ReadCsv'
urlpatterns = [
    path('upload', views.upload, name='upload'),
    path('show', views.show, name='show'),
]
