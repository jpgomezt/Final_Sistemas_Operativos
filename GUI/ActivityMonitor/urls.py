from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_processes, name='list_processes'),
    path('folder/create', views.create_folder, name='create_folder'),
    path('folder/list', views.list_folders, name='list_folders'),
    path('folder/delete/<str:folder_name>', views.delete_folder, name='delete_folder'),
    path('app/launch', views.launch_app, name='launch_app'),
    path('app/list', views.list_apps, name='list_apps'),
    path('app/kill/<int:app_pid>', views.kill_app, name='kill_app'),
]