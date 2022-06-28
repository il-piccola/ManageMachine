from django.urls import path
from . import views

app_name = 'OrderDetail'
urlpatterns = [
    path('show/<order>', views.show, name='show'),
]
