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

__author__ = 'gtsa07'


# imports 3rd party libs
import requests
from iotqatools.iot_tools import PqaTools
import urllib2

# Params GW
SERVER_ROOT = 'http://localhost:8002'

MeasuresType = {
    "UL": "/idas/2.0?apikey={}&ID={}",
    "UL2": "/d?k={}&i={}",
    "IoTUL2CmdResp": "/iot/d?k={}&i={}&c={}",
    "IoTUL2": "/iot/d?k={}&i={}",
    "IoTRepsol": "/iot/repsol",
    "IoTTT": "/iot/tt",
    "IoTEvadts": "/iot/evadts?apikey={}&ID={}",
    "RegLight": "/idas/2.0?apikey={}"
}


class Gw_Measures_Utils(object):
    """Constructor"""

    def __init__(self, **kwargs):
        self.server_root = kwargs.get('server_root', SERVER_ROOT)

    """General Methods"""

    """
    getUrl-> Return a correct URL to send measures for SBC
    type(string): measure format (UL/UL2)
    apikey(string): apikey service
    idDevice(string): id Device registed in SBC
    """

    def getUrl(self, url_type, apikey, idDevice, command=()):
        path = MeasuresType.get(url_type, False)
        url = self.server_root
        if path != False:
            if url_type == 'RegLight':
                url += path.format(apikey)
#            elif url_type == 'UL2CmdResp':
#                url += path.format(apikey, idDevice, command)
            else:
                url += path.format(urllib2.quote(apikey.encode('utf8')),
                                   urllib2.quote(idDevice.encode('utf8')),
                                   command)
        else:
            if apikey:
                url += url_type.format(apikey)
            elif idDevice:
                url += url_type.format(idDevice)
        return url

    """
    SendMeasure -> send measures simulating a device

    type(string): measure format (UL,UL2,etc)
    apikey(string): apikey service
    idDevice(string): id Device registed in SBC
    *measures(dict): dictionaries with the measures
    example:
    measure1={
        "timestamp": YYYY-MM-DDTHH:MM:SSZ, ->This param is optional
        "id": "8:1", ->Phenomenom ID (only for UL)
        "alias": "t", (mandatory)
        "value": 20 (mandatory)
    }
    """

    def sendMeasure(self, measure_type, apikey, idDevice, measures, field={}):
        url = self.getUrl(measure_type, apikey, idDevice)
        if field == 'getCmd':
            url += '&getCmd=1'
        if "ip" in field:
            url += '&ip='
            url += field["ip"]

        print 'url: ' + url
        data = self.getMeasure(measure_type, measures, field)
        res = requests.post(url, data=data)

        #log request
        PqaTools.log_requestAndResponse(url=url, headers={}, data=data, comp='IOTA', response=res, method='post')
        return res

    """
    getMeasure -> Format a measures dictionary
    type(string): measure format (UL,UL2,etc)
    measures(list): list of dictionaries with the measures
    example:
    measures=[{
        "timestamp": YYYY-MM-DDTHH:MM:SSZ, ->This param is optional
        "id": "8:1", ->Phenomenom ID
        "alias": "t",
        "value": 20
    }]
"""

    def getMeasure(self, protocol, measures, field={}):
        result = ""
        print measures
        for measure in measures:
            # Format type UL or UL2
            if protocol == "UL":
                result += "||" + str(measure.get("timestamp", "")) + "|" + str(measure.get("id", "")) + "||" + str(
                    measure.get("alias", "")) + "|" + str(measure.get("value", "")) + "#"
            elif (protocol == "UL2") | (protocol == "IoTUL2"):
                result += str(measure.get("timestamp", "")) + "|" + str(measure.get("alias", "")) + "|" + str(
                    measure.get("value", "")) + "#"
            elif protocol == "IoTRepsol":
                result2 = {}
                result2["id"] = str(measure.get("id", ""))
                if field != "from":
                    result2["from"] = "tel:" + str(measure.get("device", "")) + ";phone-context=+34"
                result2["to"] = "tel:+123123123;phone-context=+34"
                if field != "message":
                    result2["message"] = str(measure.get("message", ""))
                if field != "timestamp":
                    result2["timestamp"] = str(measure.get("timestamp", ""))
                result = str(result2)
            else:
                result = str(measure)
        if "UL" in protocol:
            result = result.rpartition("#")[0]  # delete the last "#"
        print result
        # Replace specials words and characters
        replaces = {
            "True": "1",
            "False": "0",
            "true": "1",
            "false": "0",
            ";": "/",
            "&": "|"
        }
        if not "IoT" in protocol:
            for kreplace in replaces:
                result = result.replace(kreplace, replaces[kreplace])
        else:
            result = result.replace("\'", "\"")
        return result

    def sendRegister(self, apikey, device, asset, model, phenomena):
        url = self.getUrl('RegLight', apikey, device)
        print 'url: ' + url
        uom_id = 1
        result = "<rs>"
        result += "<id href=\"1:1\">" + device + "</id>"
        result += "<id href=\"1:8\">" + asset + "</id>"
        result += "<param name=\"ModelName\">"
        result += "<text>" + model + "</text>"
        result += "</param>"
        print phenomena
        for phenom in phenomena:
            result += "<what href=\"" + str(phenom.get("href", "")) + "\" id=\"" + str(phenom.get("alias", "")) + "\"/>"
        for phenom in phenomena:
            result += "<data name=\"" + str(phenom.get("phenom", "")) + "\" id=\"" + str(
                phenom.get("alias", "")) + "\">"
            if phenom.get("uom"):
                result += "<quan uom=\"" + str(phenom.get("uom", "")) + "\">" + str(uom_id) + "</quan>"
            else:
                result += "<text>" + str(uom_id) + "</text>"
            uom_id += 1
            result += "</data>"
        result += "</rs>"
        print result
        res = requests.post(url, data=result)

        #log request
        PqaTools.log_requestAndResponse(url=url, headers={}, data=result, comp='IOTA', response=res, method='post')

        return res

    """
    GetCommand -> get commands simulating a device

    measure_type(string): measure format (UL,UL2,etc)
    apikey(string): apikey service
    idDevice(string): id Device registed in SBC
    """

    def getCommand(self, measure_type, apikey, idDevice, ip={}):
        url = self.getUrl(measure_type, apikey, idDevice)
        if ip:
            url += "&ip=" + ip
        print 'url: ' + url
        res = requests.get(url)

        #log request
        PqaTools.log_requestAndResponse(url=url, headers={}, data='', comp='IOTA', response=res, method='get')
        return res

    """
    SendCommandResponse -> Send command responses simulating a device

    measure_type(string): measure format (UL,UL2,etc)
    apikey(string): apikey service
    idDevice(string): id Device registed in SBC
    """

    def SendCmdResponse(self, measure_type, apikey, idDevice, command, response):
        url = self.getUrl(measure_type, apikey, idDevice, command)
        print 'url: ' + url
        data = str(command) + "|" + str(response)
        res = requests.post(url, data=data)

        #log request
        PqaTools.log_requestAndResponse(url=url, headers={}, data=data, comp='IOTA', response=res, method='post')
        return res
