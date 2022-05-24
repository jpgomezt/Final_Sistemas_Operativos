import os
import types
import parser
import socket
import selectors
import subprocess

sel = selectors.DefaultSelector()

HOST = "127.0.0.1"
PORT = 3343

PATH = "python /Users/jpgomezt/Projects/Final_Sistemas_Operativos/App/app.py"

running_apps = {}

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"\nClosing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            jsonRequest = parser.parseRequest(data.outb)
            if(jsonRequest["request"] == "launch_app"):
                response = {}
                response["result"], response["pid"] = launch_app()
            elif(jsonRequest["request"] == "get_apps"):
                response = {"apps": get_apps()}
            elif(jsonRequest["request"] == "kill_app"):
                response = {"result": str(kill_app(jsonRequest["app_pid"]))}
            response = bytes(str(response), 'utf-8')
            print(response)
            sock.send(response) 
            data.outb = b""

def init_socket():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Listening on {(HOST, PORT)}")
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

def launch_app():
    try:
        app = subprocess.Popen(PATH, shell=True, stdout=subprocess.DEVNULL)
        running_apps[app.pid] = app
        return str(True), app.pid
    except OSError:
        return str(False), -1

def get_apps():
    try:
        apps={}
        count = 0
        for name, app in running_apps.items():
            if(app.poll() is None):
                apps["app" + str(count)] = {"pid": app.pid, "status": "running"}
            else:
                apps["app" + str(count)] = {"pid": app.pid, "status": "stopped"}
            count += 1
        return apps
    except:
        return str(False)

def kill_app(app_pid):
    try:
        running_apps[app_pid].kill()
        running_apps.pop(app_pid)
        return True
    except OSError:
        return False

if __name__=="__main__":
    try:
        init_socket()
    finally:
        print("Killing processes")
        for app in running_apps.values():
            app.kill()