from django.urls import path
from . import views

app_name = 'MainMenu'
urlpatterns = [
    path('', views.index, name='index'),
    path('index2', views.index2, name='index2'),
    path('menu', views.menu, name='menu'),
]
