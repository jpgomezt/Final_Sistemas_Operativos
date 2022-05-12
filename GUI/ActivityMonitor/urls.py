from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_processes, name='list_processes'),
]