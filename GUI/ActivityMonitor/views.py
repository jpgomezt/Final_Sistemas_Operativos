from re import S
import socket
import json
from .forms import FolderForm
from django.shortcuts import render, redirect

HOST = "127.0.0.1"
PORT = 3337  # The port used by the server

# Create your views here.
def list_processes(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "get_processes"} 
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    processes = json.loads(strResponse)["running_processes"]
    return render(request, 'ActivityMonitor/monitor.html', {'processes': processes})

def list_folders(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "get_folders"} 
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    folders = json.loads(strResponse)["folders"]
    print(type(folders))
    print(folders)
    return render(request, 'ActivityMonitor/list_folders.html', {'folders': folders})

def create_folder(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            sock_request = {"request": "create_folder", "folder_name": form.cleaned_data.get('folder_name')} 
            jsonBytes = bytes(str(sock_request), 'utf-8') 
            sock.sendall(jsonBytes)
            response = sock.recv(1024)
            strResponse = response.decode('utf-8')
            strResponse = strResponse.replace('\'', '\"')
            print(strResponse)
            result = json.loads(strResponse)
            return redirect('list_folders')
    else:
        form = FolderForm()
    return render(request, 'ActivityMonitor/create_folder.html', {'form': form})

def delete_folder(request, folder_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "delete_folder", "folder_name": folder_name}
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    print(strResponse)
    result = json.loads(strResponse)
    return redirect('list_folders')

def list_apps(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "get_apps"} 
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    apps = json.loads(strResponse)["apps"]
    print(type(apps))
    print(apps)
    return render(request, 'ActivityMonitor/list_apps.html', {'apps': apps})

def launch_app(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "launch_app"} 
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    print(strResponse)
    result = json.loads(strResponse)
    return redirect('list_apps')

def kill_app(request, app_pid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "kill_app", "app_pid": app_pid}
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    print(strResponse)
    result = json.loads(strResponse)
    return redirect('list_apps')

def end_process(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock_request = {"request": "end_process"}
    jsonBytes = bytes(str(sock_request), 'utf-8') 
    sock.sendall(jsonBytes)
    response = sock.recv(1024)
    strResponse = response.decode('utf-8')
    strResponse = strResponse.replace('\'', '\"')
    print(strResponse)
    result = json.loads(strResponse)
    return redirect('list_processes')