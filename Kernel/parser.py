import json

def parseRequest(request):
    strRequest = request.decode('utf-8')
    strRequest = strRequest.replace('\'', '\"')
    print(strRequest)
    jsonRequest = json.loads(strRequest)
    return jsonRequest
