import os
import types
import parser
import socket
import logging
import selectors

sel = selectors.DefaultSelector()

HOST = "127.0.0.1"
PORT = 3342

PATH = "/Users/jpgomezt/Projects/Final_Sistemas_Operativos/FileManager/Files"

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
            if(jsonRequest["request"] == "create_folder"):
                write_log("FILE MANAGER: create_folder")
                response = {"result": str(create_folder(jsonRequest["folder_name"]))}
            elif(jsonRequest["request"] == "get_folders"):
                write_log("FILE MANAGER: get_folders")
                response = {"folders": get_folders()}
            elif(jsonRequest["request"] == "delete_folder"):
                write_log("FILE MANAGER: delete_folder")
                response = {"result": str(delete_folder(jsonRequest["folder_name"]))}
            elif(jsonRequest["request"] == "write_log"):
                response = {"result": str(write_log(jsonRequest["log"]))}
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

def get_folders():
    try:
        return os.listdir(PATH)
    except:
        return str(False)

def create_folder(folder_name):
    try:
        os.mkdir(PATH + "/" + folder_name)
        return True
    except OSError:
        return False

def delete_folder(folder_name):
    try:
        os.rmdir(PATH + "/" + folder_name)
        return True
    except OSError:
        return False

def write_log(log):
    try:
        logging.info(log)
        return True
    except:
        return False

if __name__=="__main__":
    logger_file = logging.basicConfig(filename=(PATH + "registros.log"), format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z', level=logging.DEBUG)
    init_socket()
