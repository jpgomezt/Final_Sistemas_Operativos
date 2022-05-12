from re import S
import socket
import json
from django.shortcuts import render

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