#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright 2015 Telefonica Investigación y Desarrollo, S.A.U

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

__author__ = 'developer'

from flask import Flask, request, Response
from sys import argv
import time

app = Flask(__name__)
port = 7100
host = '0.0.0.0'
# Arguments from command line
if len(argv) > 1:
    port = int(argv[1])


@app.route('/simulaClient/ul20Command', methods=['GET', 'POST'])
def treat_client_ul20_cmd():
    mydata = ''

    if (request.data is not None) and (len(request.data) != 0):
        mydata = request.data

    app.logger.info(str(mydata))
    for h in request.args.keys():
        if h == 'delay':
            saux = request.args[h]
            t = float(saux)
            time.sleep(t)

    command_fields = mydata.split("|");
    cmd_name = command_fields[0].split("@");
    app.logger.info(cmd_name[0])
    app.logger.info(cmd_name[1])
    if cmd_name[1] == "ping":
        cmdresp = command_fields[0] + "|ping OK"
    else:
        cmdresp = mydata

    return Response(response=cmdresp, status=200, content_type='text/plain;charset=UTF-8')


if __name__ == '__main__':
    app.run(host=host, port=port)
