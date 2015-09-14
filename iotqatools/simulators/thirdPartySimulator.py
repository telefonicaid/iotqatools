#!/usr/bin/python

__author__ = 'macs'

from flask import Flask, request, Response
from sys import argv
import random

app = Flask(__name__)

# Default arguments
port = 7010
host = '0.0.0.0'

# Arguments from command line
if len(argv) > 1:
    port = int(argv[1])


@app.route('/sync/request', methods=['POST'])
def treat_sync_request():
    global lastRequest, myResponse, cont

    cont += 1
    lastRequest = request.data
    resp = Response()
    return Response(response=myResponse, status=200, content_type='application/json', headers=resp.headers)


@app.route('/async/create', methods=['POST','GET'])
def treat_async_create():
    global asyncRequest

    uid = '12345678990'
    asyncRequest[uid] = {'state': 'P'}
    myresp = {"id": uid, "details": {"rgb" : "66CCDD", "t": 2}}
    return Response(response=myresp, status=200, content_type='application/json')


@app.route('/async/requests', methods=['POST','GET'])
def treat_async_request_all():
    global asyncRequest

    return Response(response=asyncRequest, status=200, content_type='application/json')


@app.route('/async/request/<uid>', methods=['POST','GET'])
def treat_async_request(uid):
    global asyncRequest

    return Response(response=asyncRequest[uid], status=200, content_type='application/json')


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

    resp_last = Response()
    return Response(response=lastRequest, status=200, content_type='application/json', headers=resp_last.headers)


@app.route('/count', methods=['GET'])
def count():
    global cont
    return Response(response=str(cont), status=200)


@app.route('/reset', methods=['GET'])
def reset():
    global lastRequest, cont
    lastRequest = ''
    cont = 0
    return Response(status=200)


# Globals
lastRequest = ''
responseError = ''
myResponse = '{"details": {"rgb":"66CC00","t":2}}'
cont = 0
asyncRequest = []

if __name__ == '__main__':
    app.run(host=host, port=port)
