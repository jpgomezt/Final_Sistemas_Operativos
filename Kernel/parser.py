import json
import socket
import configparser

FILE = "config.ini"

def parseRequest(request):
    strRequest = request.decode('utf-8')
    strRequest = strRequest.replace('\'', '\"')
    print(strRequest)
    jsonRequest = json.loads(strRequest)
    return jsonRequest

def request_file_manager(request):
    config = configparser.ConfigParser()
    config.read(FILE)
    server_ip, server_port = dict(config.items('FileManager'))["sever"].split(",")
    server_port = int(server_port)
    response = b''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    request = bytes(str(request), 'utf-8') 
    sock.sendall(request)
    response = sock.recv(1024)
    print("Response:", response)
    sock.close()
    return response
