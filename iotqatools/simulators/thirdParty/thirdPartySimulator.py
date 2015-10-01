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
    global last_request, cont, delay

    app.logger.info("Received sync request")
    # Increase the number of requests
    cont += 1

    # Store the last request
    last_request = request.data
    app.logger.info('Request data received: ' + last_request)

    # Set delay if needed
    if delay is not '':
        app.logger.info("Delay stated")
        sleep(int(delay))
        delay = ''

    # Retrieve request information
    service = request.headers['fiware-service']
    subservice = request.headers['fiware-servicepath']
    button_id = json.loads(request.data)['button']
    headers = {'Accept': 'application/json', 'content-type': 'application/json', 'fiware-service': service,
               'fiware-servicepath': subservice}

    # Generate sync response
    sync_response = {'externalId': generate_uid(), 'buttonId': button_id, 'details': {}}
    sync_response['details']['rgb'] = '66CCDD'
    sync_response['details']['t'] = '2'
    app.logger.info('Response sent: ' + json.dumps(sync_response))

    return Response(response=json.dumps(sync_response), status=200, headers=headers)


@app.route('/async/create', methods=['POST'])
def treat_async_create():
    global last_request

    app.logger.info("Recived async create")
    # Store the last request
    last_request = request.data
    app.logger.info('Request data received: ' + last_request)

    # Retrieve callback url and buttonId from request
    service = request.headers['fiware-service']
    subservice = request.headers['fiware-servicepath']
    url_callback = json.loads(request.data)['callback']
    button_id = json.loads(request.data)['button']
    app.logger.info('Headers received: ' + str(request.headers))

    # Compose the async response
    async_response = {'externalId': str(generate_uid()), 'buttonId': str(button_id), 'details': {}}
    async_response['details']['rgb'] = '66CCDD'
    async_response['details']['t'] = '2'

    # Invoke callback response
    t = threading.Thread(target=invoke_ca, args=(async_response, url_callback, service, subservice))
    t.start()
    return Response(response='Create Received OK', status=200)


def invoke_ca(async_response, url_callback, service, subservice):
    # Wait until request is finished
    sleep(3)

    # Send data to urlCallback
    headers = {'Accept': 'application/json', 'content-type': 'application/json', 'fiware-service': service,
               'fiware-servicepath': subservice}
    app.logger.info('Response sent to ' + url_callback + ' is: ' + json.dumps(async_response))
    app.logger.info('Headers sent: ' + str(headers))
    r = requests.post(url_callback, data=json.dumps(async_response), headers=headers)
    return r


def generate_uid():
    uid = str(random.randint(1, 9999999))
    app.logger.info('Generated uid: ' + uid)
    return uid


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
    global last_request, cont
    last_request = ''
    cont = 0
    return Response(status=200)


# Globals
last_request = ''
responseError = ''
cont = 0
delay = ''

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
