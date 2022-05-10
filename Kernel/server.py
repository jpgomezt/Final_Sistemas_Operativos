from asyncio import subprocess
from concurrent.futures import process
import os
import time
import subprocess
import socket
import selectors
import types
import parser

sel = selectors.DefaultSelector()

HOST = "127.0.0.1"
PORT = 3337

running_process = {}

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
            servers = parser.getServers(jsonRequest, "config.ini")
            response = parser.connectToServer(data.outb, servers)
            if response == b'':
                response = b'{"status" : 500, "message" : "Error"}'
                print("\nThere is no response from servers, the servers should be down")
            sock.send(response)
            data.outb = b''

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

if __name__=="__main__":
    running_process["kernel"] = os.getpid()
    gui = subprocess.Popen("python ../GUI/manage.py runserver", shell=True, stdout=subprocess.DEVNULL)
    running_process["gui"] = gui.pid
    process2 = subprocess.Popen("python ../App/app.py", shell=True, stdout=subprocess.DEVNULL)
    running_process["application"] = process2.pid
    print("kernel pid: " + str(running_process["kernel"]))
    print("gui pid: " + str(running_process["gui"]))
    print("aplication pid: " + str(running_process["application"]))
    init_socket()