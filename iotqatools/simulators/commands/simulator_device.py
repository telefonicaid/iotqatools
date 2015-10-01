#!/usr/bin/python


__author__ = 'developer'


from flask import Flask, request, Response
from sys import argv
import os
import time
from array import *

app = Flask(__name__)
port = 7100
host = '0.0.0.0'
# Arguments from command line
if len(argv) > 1:
    port = int(argv[1])

@app.route('/simulaClient/ul20Command', methods=['GET', 'POST'])
def treat_client_ul20_cmd():

    mydata = ''

    if ((request.data is not None) and (len(request.data) != 0)):
        mydata = request.data

    print str(mydata)
    for h in request.args.keys():
      if (h == 'delay'):
          saux =  request.args[h]
          t = float(saux)
          if verbose:
             print 'sleeping'
          time.sleep (t)

    command_fields = mydata.split("|");
    cmd_name = command_fields[0].split("@");
    print cmd_name[0]
    print cmd_name[1]
    if (cmd_name[1] == "ping"):
       cmdresp = command_fields[0] + "|ping OK"
    else :
       cmdresp = mydata

    return Response(response=cmdresp, status=200, content_type='text/plain;charset=UTF-8')


if __name__ == '__main__':
    app.run(host=host, port=port)
