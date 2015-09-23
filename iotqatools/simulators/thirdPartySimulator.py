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
    global last_request, sync_response, cont, delay

    print "Recived sync request"
    # Increase the number of requests
    cont += 1

    # Store the last request
    last_request = request.data

    # Set delay if needed
    if delay is not '':
        sleep(int(delay))
        delay = ''

    # Retrieve request information
    service = request.headers['fiware-service']
    subservice = request.headers['fiware-servicepath']
    button_id = json.loads(request.data)['button']
    headers = {'Accept': 'application/json', 'content-type': 'application/json', 'fiware-service': service,
               'fiware-servicepath': subservice}

    # Generate sync response
    sync_response['externalId'] = generate_uid()
    sync_response['buttonId'] = button_id
    sync_response['details'] = {}
    sync_response['details']['rgb'] = '66CCDD'
    sync_response['details']['t'] = '2'

    return Response(response=json.dumps(sync_response), status=200, headers=headers)


@app.route('/async/create', methods=['POST'])
def treat_async_create():
    global last_request, async_request, url_callback, async_response, service, subservice

    print "Recived async create"
    # Store the last request
    last_request = request.data

    # Retrieve callback url and buttonId from request
    service = request.headers['fiware-service']
    subservice = request.headers['fiware-servicepath']
    url_callback = json.loads(request.data)['callback']
    button_id = json.loads(request.data)['button']

    # Compose the async response
    async_response['externalId'] = str(generate_uid())
    async_response['buttonId'] = str(button_id)
    async_response['details'] = {}
    async_response['details']['rgb'] = '66CCDD'
    async_response['details']['t'] = '2'

    # Invoke callback response
    t = threading.Thread(target=invoke_ca)
    t.start()
    return Response(response='Create Received OK', status=200)


def invoke_ca():
    # Wait until request is finished
    sleep(3)

    # Send data to urlCallback
    headers = {'Accept': 'application/json', 'content-type': 'application/json', 'fiware-service': service,
               'fiware-servicepath': subservice}
    r = requests.post(url_callback, data=json.dumps(async_response), headers=headers)
    return r


def generate_uid():
    return str(random.randint(1, 9999999))


@app.route('/async/requests', methods=['POST', 'GET'])
def treat_async_request_all():
    global async_request

    return Response(response=str(async_request), status=200)


@app.route('/async/request/<uid>', methods=['POST', 'GET'])
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


@app.route('/setDelayToSync', methods=['GET'])
def treat_set_delay_to_sync():
    global delay

    delay = request.args.get('delay')
    return Response(response='Delay to next sync request set to ' + delay, status=200)


@app.route('/last', methods=['GET'])
def treat_last():
    global last_request

    return Response(response=last_request, status=200)


@app.route('/count', methods=['GET'])
def count():
    global cont
    return Response(response=str(cont), status=200)


@app.route('/reset', methods=['GET'])
def reset():
    global last_request, async_request, cont
    last_request = ''
    async_request = {}
    cont = 0
    return Response(status=200)


# Globals
last_request = ''
responseError = ''
sync_response = {}
async_response = {}
cont = 0
async_request = {}
service = ''
subservice = ''
url_callback = "http://localhost:9999"
delay = ''

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
