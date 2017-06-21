# -*- coding: utf-8 -*-
"""
Copyright 2016 Telefonica Investigación y Desarrollo, S.A.U

This file is part of telefonica-iot-qa-tools

iot-qa-tools is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

iot-qa-tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with iot-qa-tools.
If not, seehttp://www.gnu.org/licenses/.

For those usages not covered by the GNU Affero General Public License
please contact with::[iot_support@tid.es]
"""
__author__ = 'Iván Arias León (ivan dot ariasleon at telefonica dot com)'

import sys
import json
import BaseHTTPServer
import ssl
import time
import thread


# variables
default_payload = json.dumps({"msg":"without notification received"})
unknown_path = json.dumps({"error":"unknown path: %s"})
last_url = ""
last_headers = {}
last_payload = default_payload


def get_last_data(s):
    """
    Store the request data (method, url, path, headers, payload)
    """
    global last_url, last_headers, last_payload
    # last url
    last_url = "%s - %s://%s%s" % (s.command, s.request_version.lower().split("/")[0], s.headers["host"], s.path)

    # last headers
    for item in s.headers:
        last_headers[item] = s.headers[item]

    # last payload
    length = int(s.headers["Content-Length"])
    if length > 0:
        last_payload = str(s.rfile.read(length))

def show_last_data():
    """
    display all data from request in log
    :return: string
    """
    global last_url, last_headers, last_payload, VERBOSE, __logger__
    if VERBOSE.lower() == "true":
        print("Request data received in listener:\n Url: %s\n Headers: %s\n Payload: %s\n" % (last_url, str(last_headers), last_payload))



class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    HTTP server

    This http server is used to store the last request of all POST (in the future PUT, DELETE, PATCH, HEAD) requests,
    returns the url, headers, and the payload with the GET /last_notification request (used in CB to notifications)
    """
    def do_POST(s):
        """
        POST request
        """
        global last_headers, last_payload, last_url, get_last_data, show_last_data
        s.send_response(200)
        get_last_data(s)
        headers_prefix = u'last'
        for item in last_headers:
            s.send_header("%s-%s" % (headers_prefix, item), last_headers[item])
        s.send_header("%s-url" % headers_prefix, "%s" % (last_url))

        show_last_data()   # verify VERBOSE global variable

        s.end_headers()
        s.wfile.write(last_payload)

    def do_PUT(s):
        """
        PUT request
        """
        global last_headers, last_payload, last_url, get_last_data, show_last_data
        s.send_response(200)
        get_last_data(s)
        headers_prefix = u'last'
        for item in last_headers:
            s.send_header("%s-%s" % (headers_prefix, item), last_headers[item])
        s.send_header("%s-url" % headers_prefix, "%s" % (last_url))

        show_last_data()   # verify VERBOSE global variable

        s.end_headers()
        s.wfile.write(last_payload)

    def do_DELETE(s):
        """
        PUT request
        """
        global last_headers, last_payload, last_url, get_last_data, show_last_data
        s.send_response(200)
        get_last_data(s)
        headers_prefix = u'last'
        for item in last_headers:
            s.send_header("%s-%s" % (headers_prefix, item), last_headers[item])
        s.send_header("%s-url" % headers_prefix, "%s" % (last_url))

        show_last_data()   # verify VERBOSE global variable

        s.end_headers()
        s.wfile.write(last_payload)

    def do_PATCH(s):
        """
        PUT request
        """
        global last_headers, last_payload, last_url, get_last_data, show_last_data
        s.send_response(200)
        get_last_data(s)
        headers_prefix = u'last'
        for item in last_headers:
            s.send_header("%s-%s" % (headers_prefix, item), last_headers[item])
        s.send_header("%s-url" % headers_prefix, "%s" % (last_url))

        show_last_data()   # verify VERBOSE global variable

        s.end_headers()
        s.wfile.write(last_payload)

    def do_GET(s):
        """
        GET request
        """
        global last_headers, last_payload, unknown_path, last_url
        s.send_response(200)
        if s.path == "/last_notification":
            headers_prefix = u'last'
            for item in last_headers:
                s.send_header("%s-%s" % (headers_prefix, item), last_headers[item])
            s.send_header("%s-url" % headers_prefix, "%s" % last_url)
        elif s.path == "/reset":
            last_url = ""
            last_headers = {}
            last_payload = default_payload
        else:
             last_payload = unknown_path % s.path

        show_last_data()   # verify VERBOSE global variable

        s.end_headers()
        s.wfile.write(last_payload)

def init_server(port, https):
    """
    Function to init the server

    :param port: the port to use for the server
    :param https: True if HTTPS has to be used, false otherwise

    NOTE: This function relies in several global variables, which  probably it is not a good practise, but it suffices
    """

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((ip_bind, port), MyHandler)

    if https:
        # Based on https://anvileight.com/blog/2016/03/20/simple-http-server-with-python/
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=key_file, certfile=cert_file, server_side=True)
        print("HTTPS Server Started using the %d port" % port)
    else:
        print("HTTP Server Started using the %d port" % port)

    httpd.serve_forever()
    httpd.server_close()   # This line is never executed, but we add here for completeness ;)


port = sys.argv[1] if (len(sys.argv) >= 2) else "1044"
VERBOSE = sys.argv[2] if (len(sys.argv) >= 3) else "True"
key_file = sys.argv[3] if (len(sys.argv) >= 4) else None
cert_file = sys.argv[4] if (len(sys.argv) >= 5) else None

ip_bind = "0.0.0.0"
print "Usage:\n"\
      "    python notification_listener.py <port> <debug> <key_file> <cert_file>\n" \
      "      - port: server port used [OPTIONAL] (default: 1044)\n" \
      "      - debug: show request data by console (boolean) [OPTIONAL] (default: True)\n" \
      "      - key_file: path to key file (HTTPS) [OPTIONAL] (default: None)\n" \
      "      - cert_file: path to cert file (HTTPS) [OPTIONAL] (default: None)\n\n"
print " ******* CRTL - C to stop the server ******\n\n"

# We have to run each server in a separate thread, see https://stackoverflow.com/questions/44651542/
#
# HTTPS server runs in HTTP port + 10000. Alternativelly, we could add a new parameter but that makes
# more complex the CLI.
thread.start_new_thread(init_server, (int(port), False, ))
if key_file is not None and cert_file is not None:
    thread.start_new_thread(init_server, (int(port) + 10000, True, ))

try:
    while 1:
        time.sleep(10)
except KeyboardInterrupt:
   print("Closing listener...")
   exit(0)


