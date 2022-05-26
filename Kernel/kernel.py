import os
import types
import parser
import socket
import selectors
import subprocess

sel = selectors.DefaultSelector()

HOST = "127.0.0.1"
PORT = 3337

running_processes = {}

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
            if(jsonRequest["request"] == "get_processes"):
                response = {"running_processes": get_processes()}
                response = bytes(str(response), 'utf-8')
                parser.log_action({"request": "write_log", "log": "KERNEL: " + jsonRequest["request"]})
            elif(jsonRequest["request"] == "end_process"):
                parser.log_action({"request": "write_log", "log": "KERNEL: " + jsonRequest["request"]})
                end_process()
            elif(jsonRequest["request"] == "get_folders" or jsonRequest["request"] == "create_folder" or jsonRequest["request"] == "delete_folder"):
                response = parser.request_file_manager(jsonRequest)
            elif(jsonRequest["request"] == "get_apps" or jsonRequest["request"] == "launch_app" or jsonRequest["request"] == "kill_app"):
                response = parser.request_app_manager(jsonRequest)
                parser.log_action({"request": "write_log", "log": "APP MANAGER: " + jsonRequest["request"]})
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

def init_processes():
    gui = subprocess.Popen("python ../GUI/manage.py runserver", shell=True, stdout=subprocess.DEVNULL)
    running_processes["gui"] = gui
    app_manager = subprocess.Popen("python ../App/app_manager.py", shell=True, stdout=subprocess.DEVNULL)
    running_processes["app manager"] = app_manager
    file_manager = subprocess.Popen("python ../FileManager/file_manager.py", shell=True, stdout=subprocess.DEVNULL)
    running_processes["file manager"] = file_manager

def get_processes():
    processes={}
    for name, process in running_processes.items():
        print(name + ": " + str(process.pid))
        if(process.poll() is None):
            processes[name] = {"pid": process.pid, "status": "running"}
        else:
            processes[name] = {"pid": process.pid, "status": "stopped"}
    processes["kernel"] = {"pid": os.getpid(), "status": "running"}
    return processes

def end_process():
    for process in running_processes.values():
        process.kill()
    os._exit()

if __name__=="__main__":
    try:
        init_processes()
        print(get_processes())
        init_socket()
    finally:
        print("Killing processes")
        for process in running_processes.values():
            process.kill()