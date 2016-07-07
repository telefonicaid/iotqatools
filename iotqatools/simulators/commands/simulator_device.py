#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright 2015 Telefonica Investigación y Desarrollo, S.A.U

This file is part of telefonica-iotqatools

iotqatools is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

iotqatools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with iotqatools.
If not, seehttp://www.gnu.org/licenses/.

For those usages not covered by the GNU Affero General Public License
please contact with::[iot_support@tid.es]
"""

__author__ = 'developer'

from flask import Flask, request, Response
from sys import argv
import time
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
port = 7100
host = '0.0.0.0'

# Arguments from command line
if len(argv) > 1:
    port = int(argv[1])


@app.route('/simulaClient/ul20Command', methods=['GET', 'POST'])
def treat_client_ul20_cmd():
    app.logger.info('Received command to {}'.format(request.url))

    # Extraxt delay parameter if exists. Simulator waits the delay before it responds
    if request.args.get('delay'):
        delay = int(request.args.get('delay'))
        app.logger.debug('Waiting {} seconds ...'.format(delay))
        time.sleep(delay)
    else:
        app.logger.info('No delay provided as parameter')

    # Check if command is sent and compose response
    if (request.data is not None) and (len(request.data) != 0):
        my_data = request.data
        app.logger.debug('Data received: {}'.format(my_data))
        command_fields = my_data.split("|")
        cmd_name = command_fields[0].split("@")
        cmd_resp = command_fields[0] + "|" + cmd_name[1] + " OK"
        app.logger.debug('Data responded: {}'.format(cmd_resp))
        return Response(response=cmd_resp, status=200, content_type='text/plain;charset=UTF-8')
    else:
        error_message = 'No data provided in the command'
        app.logger.error(error_message)
        return Response(response=error_message, status=400, content_type='text/plain;charset=UTF-8')


@app.route('/simulaClient/ul20CommandError', methods=['GET', 'POST'])
def treat_client_ul20_cmd_error():
    app.logger.info('Received command to {}'.format(request.url))

    # Check if command is sent and compose response
    if (request.data is not None) and (len(request.data) != 0):
        my_data = request.data
        app.logger.debug('Data received: {}'.format(my_data))
        command_fields = my_data.split("|")
        cmd_name = command_fields[0].split("@")
        cmd_resp = command_fields[0] + "|" + cmd_name[1] + " ERROR, Command error"
        app.logger.debug('Data responded: {}'.format(cmd_resp))
        return Response(response=cmd_resp, status=500, content_type='text/plain;charset=UTF-8')
    else:
        error_message = 'No data provided in the command'
        app.logger.error(error_message)
        return Response(response=error_message, status=400, content_type='text/plain;charset=UTF-8')


if __name__ == '__main__':
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = RotatingFileHandler('simulator_device.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(host=host, port=port, debug=True)
