#!/usr/bin/python
# -*- coding: latin-1 -*-
# Copyright 2017 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of telefonica-iot-qa-tools.
#
# telefonica-iot-qa-tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# telefonica-iot-qa-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with telefonica-iot-qa-tools. If not, see http://www.gnu.org/licenses/.
#
# For those usages not covered by this license please contact with
# iot_support at tid dot es

__author__ = 'fermin'

# Food for thought: we assume that HTTP requests have always Fiware-Service and Fiware-ServicePath
# headers. We take them without any checking, e.g.:
#
#   serv = request.headers['fiware-service']
#   subserv = request.headers['fiware-servicepath']
#
# It seems that for the usage of this program in the context of e2e context is ok. However,
# take note of this if used in other context where this condition can not be assured

from OpenSSL import SSL
from flask import Flask, request, Response, jsonify
from getopt import getopt, GetoptError
import sys
import os

def usage_and_exit(msg):
    """
    Print usage message and exit"

    :param msg: optional error message to print
    """

    if msg != '':
        print msg
        print

    usage()
    sys.exit(1)


def usage():
    """
    Print usage message
    """

    print 'Usage: %s --host <host> --port <port> --url <server url> -v -u' % os.path.basename(__file__)
    print ''
    print 'Parameters:'
    print "  --host <host>: host to use (default is '0.0.0.0')"
    print "  --port <port>: port to use (default is 1028)"
    print "  --url <server url>: server URL to use (default is /accumulate)"
    print "  --https: start in https"
    print "  --key: key file (only used if https is enabled)"
    print "  --cert: cert file (only used if https is enabled)"
    print "  -v: verbose mode"
    print "  -u: print this usage message"


def store(d, notif, serv, subserv):
    """
    Stores notification into notifications dictionary, creating intermediate sub-dicts if needed

    :param d: dictionary to store notification
    :param notif: notification store
    :param serv: service
    :param subserv: subservice
    """

    # Check service existence in dictionary, creating if needed
    if serv not in d:
        d[serv] = {}

    # Check subservice existence in dictionary, creating if needed
    if subserv not in d[serv]:
        d[serv][subserv] = []

    d[serv][subserv].append(notif)


def get_last(d, serv, subserv):
    """
    Return last received notification per service and subservice

    :param d: dictionary whith stores notifications
    :param serv: service
    :param subserv: subservice
    :return the received notification or empty string if serv/subserv is not found
    """

    if serv not in d:
        return ''

    if subserv not in d[serv]:
        return ''

    l = len(d[serv][subserv])

    return d[serv][subserv][l - 1]


def get_count(d, serv, subserv):
    """
    Return number of received notifications per service and subservice

    :param d: dictionary whith stores notifications
    :param serv: service
    :param subserv: subservice
    :return the number of received notification or 0 if serv/subserv is not found
    """

    if serv not in d:
        return 0

    if subserv not in d[serv]:
        return 0

    return len(d[serv][subserv])


# Default arguments
port       = 10031
host       = '0.0.0.0'
server_url = '/notify'
verbose    = 0
https      = False
key_file   = None
cert_file  = None

try:
    opts, args = getopt(sys.argv[1:], 'vu', ['host=', 'port=', 'url=', 'https', 'key=', 'cert=' ])
except GetoptError:
    usage_and_exit('wrong parameter')

for opt, arg in opts:
    if opt == '-u':
        usage()
        sys.exit(0)
    elif opt == '--host':
        host = arg
    elif opt == '--url':
        server_url = arg
    elif opt == '--port':
        try:
            port = int(arg)
        except ValueError:
            usage_and_exit('port parameter must be an integer')
    elif opt == '-v':
        verbose = 1
    elif opt == '--https':
        https = True
    elif opt == '--key':
        key_file = arg
    elif opt == '--cert':
        cert_file = arg
    else:
        usage_and_exit()

if https:
    if key_file is None or cert_file is None:
        print "if --https is used then you have to provide --key and --cert"
        os.exit(1)

if verbose:
    print "verbose mode is on"
    print "port: " + str(port)
    print "host: " + str(host)
    print "server_url: " + str(server_url)
    print "https: " + str(https)
    print "key file: " + str(key_file)
    print "cert file: " + str(cert_file)

app = Flask(__name__)

@app.route(server_url, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@app.route(server_url + '/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def process_notification(path=None):

    global notif_dict

    serv = request.headers['fiware-service']
    subserv = request.headers['fiware-servicepath']

    notif = {
        'verb': request.method,
        'url': request.base_url,
        'headers': dict(request.headers),
        'query_string': request.query_string,
        'payload': request.data
    }

    store(notif_dict, notif, serv, subserv)

    return Response(status=200)

@app.route('/last_notification', methods=['GET'])
def last_notification():

    global notif_dict

    serv = request.headers['fiware-service']
    subserv = request.headers['fiware-servicepath']

    s = get_last(notif_dict, serv, subserv)

    return jsonify(s)

@app.route('/count', methods=['GET'])
def count():
    global notif_dict

    serv = request.headers['fiware-service']
    subserv = request.headers['fiware-servicepath']

    return str(get_count(notif_dict, serv, subserv))

@app.route('/reset', methods=['GET'])
def reset():
    global notif_dict
    notif_dict = {}
    return Response(status=200)

# This is the key dictionary to store all received notifications. It is a double-key structure,
# first key is service, second key is service which element is a notifications list. Each
# item in this list includes the following fields:
#
# {
#   "verb": "...",
#   "url": "...",
#   "query_string": "...",
#   "headers: {
#      <key-values for headers>
#   },
#   "payload": as text
# }
#
# Note payload is not enough, given that in custom notification tests we may need to check more things
notif_dict = {}

if __name__ == '__main__':
    if (https):
      context = SSL.Context(SSL.SSLv23_METHOD)
      context.use_privatekey_file(key_file)
      context.use_certificate_file(cert_file)
      app.run(host=host, port=port, debug=False, ssl_context=context)
    else:
      app.run(host=host, port=port, debug=True)
