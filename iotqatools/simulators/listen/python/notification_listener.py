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


# variables
last_url = ""
last_headers = {}
last_payload = json.dumps({"msg":"without notification received"})
unknown_path = json.dumps({"error":"unknown path: %s"})

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

    def do_GET(s):
        """
        GET request
        """
        global last_headers, last_payload, unknown_path, last_url
        s.send_response(200)
        if s.path != "/last_notification":
            last_payload = unknown_path % s.path
        else:
            headers_prefix = u'last'
            for item in last_headers:
                s.send_header("%s-%s" % (headers_prefix, item), last_headers[item])
            s.send_header("%s-url" % headers_prefix, "%s" % last_url)

        show_last_data()   # verify VERBOSE global variable

        s.end_headers()
        s.wfile.write(last_payload)



port = sys.argv[1] if (len(sys.argv) >= 2) else "1044"
VERBOSE = sys.argv[2] if (len(sys.argv) >= 3) else "True"
ip_bind = "0.0.0.0"
print "Usage:\n"\
      "    python notification_listener.py <port> <Debug>\n" \
      "      - port: server port used [OPTIONAL] (default: 1044)\n" \
      "      - debug: show request data by console (boolean) [OPTIONAL] (default: True)\n\n"
print " ******* CRTL - C to stop the server ******\n\n"
server_class = BaseHTTPServer.HTTPServer
httpd = server_class((ip_bind, int(port)), MyHandler)
print("HTTP Server Started using the %s port" % port)
try:
   httpd.serve_forever()
except KeyboardInterrupt:
   exit(0)
   print("Closing the HTTP server...")
httpd.server_close()
print("HTTP Server Stopped")
