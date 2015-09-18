#!/usr/bin/python


__author__ = 'macs'

from flask import Flask, request, Response, g
from sys import argv
from time import sleep
import threading
import random
import json
import requests

app = Flask(__name__)

# Default arguments
port = 6500
host = '127.0.0.1'

# Arguments from command line
if len(argv) > 1:
    port = int(argv[1])


@app.route('/sync/request', methods=['POST'])
def treat_sync_request():
    global lastRequest, sync_response, cont

    print "Recived sync request"
    #Increase the number of requests
    cont += 1
    #Store the last request
    lastRequest = request.data
    print request.data
    return Response(response=sync_response, status=200, content_type='application/json')


@app.route('/async/create', methods=['POST'])
def treat_async_create():
    global lastRequest, async_request, url_callback, async_response

    print "Recived async create"
    #Store the last request
    lastRequest = request.data
    #generates the externalId
    uid = str(random.randint(1, 9999999))
    #Retrieve callback url and buttonId from request
    url_callback = json.loads(request.data)['callbackUrl']
    button_id = json.loads(request.data)['buttonId']
    async_response['externalId'] = str(uid)
    async_response['buttonId'] = str(button_id)
    async_response['details'] = {}
    async_response['details']['rgb'] = '66CCDD'
    async_response['details']['t'] = '2'
    print str(async_response)
    #Invoke callback response
    t = threading.Thread(target=invoke_ca)
    t.start()
    return Response(response='Create Received OK', status=200)


def invoke_ca():
    #Wait until request is finished
    sleep(3)
    #Send data to urlCallback
    headers = {'Accept': 'application/json', 'content-type': 'application/json'}
    r = requests.post(url_callback, data=json.dumps(async_response), headers=headers)
    return r


@app.route('/async/requests', methods=['POST','GET'])
def treat_async_request_all():
    global async_request

    return Response(response=str(async_request), status=200)


@app.route('/async/request/<uid>', methods=['POST','GET'])
def treat_async_request(uid):
    global async_request

    return Response(response=async_request[uid], status=200, content_type='application/json')


@app.route('/setResponseToError', methods=['GET'])
def treat_set_response_to_error():
    global responseError, myResponse

    myResponse = '{"error": "GUH-1", "details": {"rgb": "CC0000", "t": 3}}'
    return Response(response='Simulator set to Error', status=200)


@app.route('/setResponseToOk', methods=['GET'])
def treat_set_response_to_ok():
    global responseError, myResponse

    myResponse = '{"details": {"rgb":"66CC00","t":2}}'
    return Response(response='Simulator set to OK', status=200)


@app.route('/last', methods=['GET'])
def treat_last():
    global lastRequest

    return Response(response=lastRequest, status=200)


@app.route('/count', methods=['GET'])
def count():
    global cont
    return Response(response=str(cont), status=200)


@app.route('/reset', methods=['GET'])
def reset():
    global lastRequest, async_request, cont
    lastRequest = ''
    async_request = {}
    cont = 0
    return Response(status=200)


# Globals
lastRequest = ''
responseError = ''
sync_response = '{"details": {"rgb":"66CC00","t":2}}'
async_response = {}
cont = 0
async_request = {}
url_callback = "http://localhost:9999"


if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
