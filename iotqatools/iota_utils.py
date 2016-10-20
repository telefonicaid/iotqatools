# -*- coding: utf-8 -*-
"""
Copyright 2015 Telefonica Investigaci�n y Desarrollo, S.A.U

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

__author__ = 'gtsa07'

# Standard library imports
import json

# 3rd party libraries
import requests
from iotqatools.iot_tools import PqaTools

# Params APIREST
SERVER_ROOT = 'http://localhost:5371/m2m/v2'
SERVER_ROOT_SECURE = 'http://localhost:5371/secure/m2m/v2'
SERVICES_DETAIL = "services"
DEVICES_DETAIL = "devices"
SERVICE_HEADER = 'Fiware-Service'
SERVICE_PATH_HEADER = 'Fiware-ServicePath'
DEF_ENTITY_TYPE = 'thing'
CBROKER_URL = 'http://127.0.0.1:1026'
TOKEN = ''

URLTypes = {
    "IoTUL2": "/iot/d",
    "IoTRepsol": "/iot/repsol",
    "IoTModbus": "/iot/tgrepsol",
    "IoTEvadts": "/iot/evadts",
    "IoTTT": "/iot/tt",
    "IoTMqtt": "/iot/mqtt"
}

URLProtocolTypes = {
    "PDI-IoTA-UltraLight": "/iot/d",
    "PDI-SMS-REPSOL": "/iot/repsol",
    "PDI-MODBUS-REPSOL": "/iot/tgrepsol",
    "PDI-EVADTS": "/iot/evadts",
    "PDI-IoTA-ThinkingThings": "/iot/tt",
    "PDI-IoTA-MQTT-UltraLightt": "/iot/mqtt"
}

ProtocolTypes = {
    "IoTUL2": "PDI-IoTA-UltraLight",
    "IoTTT": "PDI-IoTA-ThinkingThings",
    "IoTMqtt": "PDI-IoTA-MQTT-UltraLight"
}


class Rest_Utils_IoTA(object):
    """Constructor"""

    def __init__(self, **kwargs):
        self.server_root = kwargs.get('server_root', SERVER_ROOT)
        self.server_root_secure = kwargs.get('server_root_secure', SERVER_ROOT_SECURE)
        self.services = kwargs.get('services', SERVICES_DETAIL)
        self.srv_header = kwargs.get('srv_header', SERVICE_HEADER)
        self.srv_path_header = kwargs.get('srv_path_header', SERVICE_PATH_HEADER)
        self.devices = kwargs.get('devices', DEVICES_DETAIL)
        self.def_entity_type = kwargs.get('def_entity_type', DEF_ENTITY_TYPE)
        self.cbroker = kwargs.get('cbroker', CBROKER_URL)
        self.token = kwargs.get('token', TOKEN)

    """General Methods"""

    """
    compose_url-> format patterns to create url
        patterns(list): list with the level of the url. Example: ['path1','path2']-> SERVER_ROOT/path1/path2
    """

    def compose_url(self, patterns, secure=False):
        url = self.server_root_secure if secure else self.server_root
        for pattern in patterns:
            url += "/" + str(pattern)
        return url

    def compose_headers(self, headers):
        headers["Content-Type"] = "application/json"
        if self.token:
            headers["X-Auth-Token"] = self.token
        return headers

    """
    decoratorApi-> use compose_url and add the headers,params and body to complete the requests.
                   This decorator allows methods may have a variable number of arguments.
                   This is important in order to introduce the url's patterns and headers or params.
                   Arguments:
                   *patterns: path levels in the API separated for ',' to introduce in the method compose_url
                   **headers: dictionary with headers called headers
                   **params: dictionary with params called params
                   **data: dictionary with the body of request called data
                   Example: api_get("path1","path2",headers={"Content-Type": "application/json"})
    """

    def decoratorApi(func):
        def wrapper(self, *args, **kwargs):
            if 'headers' in kwargs and 'X-Auth-Token' in kwargs['headers']:
                path = self.compose_url(args, secure=True)
            else:
                path = self.compose_url(args)
            if 'data' in kwargs:
                kwargs['data'] = json.dumps(kwargs['data'])
            return func(self, path, **kwargs)

        return wrapper

    # See decoratorAPI comments
    @decoratorApi
    def api_get(self, path, headers={}, params={}):
        res = None

        try:
            # clean content_type in not allowed requests
            if "content-type" in headers:
                params["headers"].pop("content-type", None)
            elif "Content-Type" in headers:  # used in Requests library version 2.11.1 or higher
                params["headers"].pop("Content-Type", None)

            res = requests.get(url=path,
                               headers=headers,
                               params=params)

        except requests.exceptions.Timeout:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data='',
                                            comp='IOTA',
                                            response="TIMEOUT",
                                            method='get')

        except requests.exceptions.RequestException as e:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data='',
                                            comp='IOTA',
                                            response=e, method='get')
            return "ERROR"

        # log request
        PqaTools.log_requestAndResponse(url=path,
                                        headers=headers,
                                        params=params,
                                        data='',
                                        comp='IOTA',
                                        response=res,
                                        method='get')
        return res


    # See decoratorAPI comments
    @decoratorApi
    def api_post(self, path, headers={}, params={}, data={}):
        res = None
        try:
            res = requests.post(url=path,
                                data=data,
                                headers=headers,
                                params=params)

        except requests.exceptions.Timeout:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data=data,
                                            comp='IOTA',
                                            response="TIMEOUT",
                                            method='post')

        except requests.exceptions.RequestException as e:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data=data,
                                            comp='IOTA',
                                            response=e,
                                            method='post')
            return "ERROR"

        # log request
        PqaTools.log_requestAndResponse(url=path,
                                        headers=headers,
                                        params=params,
                                        data=data,
                                        comp='IOTA',
                                        response=res,
                                        method='post')
        return res

    # See decoratorAPI comments
    @decoratorApi
    def api_put(self, path, headers={}, params={}, data={}):
        res = None
        try:
            res = requests.put(url=path,
                               data=data,
                               headers=headers,
                               params=params)

        except requests.exceptions.Timeout:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data=data,
                                            comp='IOTA',
                                            response="TIMEOUT",
                                            method='put')

        except requests.exceptions.RequestException as e:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data=data,
                                            comp='IOTA',
                                            response=e, method='put')
            return "ERROR"

            # log request
        PqaTools.log_requestAndResponse(url=path,
                                        headers=headers,
                                        params=params, data=data,
                                        comp='IOTA',
                                        response=res,
                                        method='put')
        return res

    # See decoratorAPI comments
    @decoratorApi
    def api_delete(self, path, headers={}, params={}):
        res = None
        try:
            # clean content_type in not allowed requests
            if "content-type" in headers:
                params["headers"].pop("content-type", None)
            elif "Content-Type" in headers:  # used in Requests library version 2.11.1 or higher
                params["headers"].pop("Content-Type", None)

            res = requests.delete(url=path,
                                  headers=headers,
                                  params=params)
        except requests.exceptions.Timeout:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data='', comp='IOTA',
                                            response="TIMEOUT",
                                            method='delete')

        except requests.exceptions.RequestException as e:
            PqaTools.log_requestAndResponse(url=path,
                                            params=params,
                                            headers=headers,
                                            data='',
                                            comp='IOTA',
                                            response=e, method='delete')
            return "ERROR"

        # log request
        PqaTools.log_requestAndResponse(url=path,
                                        params=params,
                                        headers=headers,
                                        data='',
                                        comp='IOTA',
                                        response=res,
                                        method='delete')
        return res

    """Version Methods"""

    def version(self, headers={}):
        """
        Get IOTA version
        """
        headers = self.compose_headers(headers)
        res = self.api_get("about", headers=headers)
        return res

    """Services Methods"""

    def get_listServices(self, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_get(self.services, headers=headers)
        return res

    def get_service(self, nameService, headers={}, params={}):
        headers = self.compose_headers(headers)
        if nameService:
            res = self.api_get(self.services, nameService, headers=headers)
        else:
            res = self.api_get(self.services, headers=headers, params=params)
        return res

    def post_service(self, json, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_post(self.services, headers=headers, data=json)
        return res

    def put_service(self, nameService, json, headers={}, params={}):
        headers = self.compose_headers(headers)
        if nameService:
            res = self.api_put(self.services, nameService, headers=headers, data=json)
        else:
            res = self.api_put(self.services, headers=headers, params=params, data=json)
        return res

    def delete_service(self, nameService={}, headers={}, params={}):
        headers = self.compose_headers(headers)
        if nameService:
            res = self.api_delete(self.services, nameService, headers=headers)
        else:
            res = self.api_delete(self.services, headers=headers, params=params)
        return res

    """Devices Methods"""

    def get_listDevices(self, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_get(self.devices, headers=headers, params=params)
        return res

    def get_device(self, nameDevice, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_get(self.devices, nameDevice, headers=headers, params=params)
        return res

    def post_device(self, json, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_post(self.devices, headers=headers, data=json)
        return res

    def put_device(self, nameDevice, json, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_put(self.devices, nameDevice, headers=headers, params=params, data=json)
        return res

    def delete_device(self, nameDevice, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_delete(self.devices, nameDevice, headers=headers, params=params)
        return res

    """Complex Services Methods"""

    def service_created(self, service_name, service_path={}, resource={}, keystone_token={}):
        headers = {}
        params = {}
        headers[self.srv_header] = str(service_name)
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
        else:
            headers[self.srv_path_header] = '/'
        if resource:
            params['resource'] = resource
        if keystone_token:
            self.token = keystone_token
        service = self.get_service('', headers, params)
        if service.status_code == 200:
            serv = service.json()
            if serv['count'] == 1:
                return True
            else:
                return False
        else:
            return False

    def create_service(self, service_name, protocol, attributes={}, static_attributes={}, cbroker={}):
        headers = {}
        headers[self.srv_header] = service_name
        headers[self.srv_path_header] = '/'
        resource = URLTypes.get(protocol)
        if (protocol == 'IotTT') | (protocol == 'IoTRepsol') | (protocol == 'IoTModbus'):
            apikey = ''
        else:
            apikey = 'apikey_' + str(service_name)
        service = {
            "services": [
                {
                    "apikey": apikey,
                    "resource": resource
                }
            ]
        }
        if cbroker:
            service['services'][0]['cbroker'] = cbroker
        else:
            service['services'][0]['cbroker'] = self.cbroker
        if attributes:
            service['services'][0]['attributes'] = attributes
        if static_attributes:
            service['services'][0]['static_attributes'] = static_attributes
        req = self.post_service(service, headers)
        return req

    def create_service_with_params(self, service_name, service_path, resource={}, apikey={}, cbroker={}, entity_type={},
                                   token={}, attributes={}, static_attributes={}, protocol={}, keystone_token={}):
        headers = {}
        if not service_name == 'void':
            headers[self.srv_header] = service_name
        if not service_path == 'void':
            headers[self.srv_path_header] = str(service_path)
        service = {
            "services": [
                {
                }
            ]
        }
        if resource:
            if not resource == 'void':
                if not resource == 'null':
                    service['services'][0]['resource'] = resource
            else:
                service['services'][0]['resource'] = ""
        if apikey:
            if not apikey == 'null':
                service['services'][0]['apikey'] = apikey
        else:
            service['services'][0]['apikey'] = ""
        if cbroker:
            if not cbroker == 'null':
                service['services'][0]['cbroker'] = cbroker
        else:
            service['services'][0]['cbroker'] = ""
        if entity_type:
            service['services'][0]['entity_type'] = entity_type
        if token:
            service['services'][0]['token'] = token
        if attributes:
            service['services'][0]['attributes'] = attributes
        if static_attributes:
            service['services'][0]['static_attributes'] = static_attributes
        if protocol:
            if not protocol == 'void':
                if not protocol == 'null':
                    resource = URLTypes.get(protocol)
                    prot = ProtocolTypes.get(protocol)
                    if not prot:
                        prot = protocol
                    service['services'][0]['protocol'] = [prot]
            else:
                resource = protocol
                service['services'][0]['protocol'] = []
        if keystone_token:
            self.token = keystone_token
        req = self.post_service(service, headers)
        return req

    def get_service_with_params(self, service_name, service_path={}, resource={}, limit={}, offset={}, protocol={}):
        headers = {}
        params = {}
        if not service_name == 'void':
            headers[self.srv_header] = str(service_name)
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
            else:
                headers[self.srv_path_header] = '/'
        if resource:
            params['resource'] = resource
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if protocol:
            prot = ProtocolTypes.get(protocol)
            if not prot:
                prot = protocol
            params['protocol'] = prot
        req = self.get_service('', headers, params)
        return req

    def update_service_with_params(self, json, service_name, service_path={}, resource={}, apikey={}):
        params = {}
        headers = {}
        if not service_name == 'void':
            headers[self.srv_header] = service_name
        if resource:
            params['resource'] = resource
        if apikey:
            params['apikey'] = apikey
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
            else:
                headers[self.srv_path_header] = '/'
        else:
            headers[self.srv_path_header] = '/'
        print params
        req = self.put_service('', json, headers, params)
        return req

    def delete_service_with_params(self, service_name, service_path={}, resource={}, apikey={}, device={},
                                   keystone_token={}):
        params = {}
        headers = {}
        if not service_name == 'void':
            headers[self.srv_header] = service_name
        if resource:
            params['resource'] = resource
        if apikey:
            params['apikey'] = apikey
        if device:
            params['device'] = device
        if keystone_token:
            self.token = keystone_token
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
            else:
                headers[self.srv_path_header] = '/'
        else:
            headers[self.srv_path_header] = '/'
        req = self.delete_service('', headers, params)
        return req

    """Complex Devices Methods"""

    def device_created(self, service_name, device_name, service_path={}, keystone_token={}):
        headers = {}
        headers[self.srv_header] = str(service_name)
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
        else:
            headers[self.srv_path_header] = '/'
        if keystone_token:
            self.token = keystone_token
        device = self.get_device(device_name, headers)
        if device.status_code == 200:
            data = json.loads(device.text)
            if "count" in data:
                return data["count"] > 0
            else:
                return True
        else:
            return False

    def create_device(self, service_name, device_name, service_path={}, endpoint={}, commands={}, entity_name={},
                      entity_type={}, attributes={}, static_attributes={}, protocol={}, keystone_token={}):
        headers = {}
        if not service_name == 'void':
            headers[self.srv_header] = str(service_name)
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
        else:
            headers[self.srv_path_header] = '/'
        device = {
            "devices": [
                {
                }
            ]
        }
        if device_name:
            if device_name == 'void':
                device_name = ""
            device['devices'][0]['device_id'] = device_name
        if commands:
            device['devices'][0]['commands'] = commands
        if endpoint:
            device['devices'][0]['endpoint'] = endpoint
        if entity_type:
            device['devices'][0]['entity_type'] = entity_type
        if entity_name:
            device['devices'][0]['entity_name'] = entity_name
        if attributes:
            device['devices'][0]['attributes'] = attributes
        if static_attributes:
            device['devices'][0]['static_attributes'] = static_attributes
        if protocol:
            if protocol == "void":
                protocol = ""
            device['devices'][0]['protocol'] = protocol
        if keystone_token:
            self.token = keystone_token
        req = self.post_device(device, headers)
        return req

    def get_device_with_params(self, service_name, device_name, service_path={}, protocol={}, keystone_token={}):
        headers = {}
        params = {}
        if not service_name == 'void':
            headers[self.srv_header] = str(service_name)
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
            else:
                headers[self.srv_path_header] = '/'
        if protocol:
            prot = ProtocolTypes.get(protocol)
            if not prot:
                prot = protocol
            params['protocol'] = prot
        if keystone_token:
            self.token = keystone_token
        req = self.get_device(device_name, headers, params)
        return req

    def get_devices_with_params(self, service_name, service_path={}, protocol={}, entity={}, detailed={}, limit={},
                                offset={}, keystone_token={}):
        headers = {}
        params = {}
        if not service_name == 'void':
            headers[self.srv_header] = str(service_name)
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
            else:
                headers[self.srv_path_header] = '/'
        if protocol:
            prot = ProtocolTypes.get(protocol)
            if not prot:
                prot = protocol
            params['protocol'] = prot
        if detailed:
            params['detailed'] = detailed
        if entity:
            params['entity'] = entity
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if keystone_token:
            self.token = keystone_token
        req = self.get_listDevices(headers, params)
        return req

    def update_device_with_params(self, json, device_name, service_name, service_path={}, protocol={},
                                  keystone_token={}):
        params = {}
        headers = {}
        if not service_name == 'void':
            headers[self.srv_header] = service_name
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
            else:
                headers[self.srv_path_header] = '/'
        if protocol:
            prot = ProtocolTypes.get(protocol)
            if not prot:
                prot = protocol
            params['protocol'] = prot
        if keystone_token:
            self.token = keystone_token
        req = self.put_device(device_name, json, headers, params)
        return req

    def delete_device_with_params(self, device_name, service_name, service_path={}, protocol={}, keystone_token={},
                                  resource={}):
        params = {}
        headers = {}
        if not service_name == 'void':
            headers[self.srv_header] = service_name
        if service_path:
            if not service_path == 'void':
                headers[self.srv_path_header] = str(service_path)
        else:
            headers[self.srv_path_header] = '/'
        if protocol:
            prot = ProtocolTypes.get(protocol)
            if not prot:
                prot = protocol
            params['protocol'] = prot
        if resource:
            params['resource'] = resource
        if keystone_token:
            self.token = keystone_token
        req = self.delete_device(device_name, headers, params)
        return req

    def get_protocols(self, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_get("protocols", headers=headers)
        return res

    def get_identifier(self, headers={}, params={}):
        headers = self.compose_headers(headers)
        res = self.api_get('about', headers=headers)
        if res.status_code == 200:
            ind1 = res.content.find("identifier:")
            if (ind1 > 0):
                ind2 = res.content.find(" ", ind1)
                return res._content[ind1 + 11:ind2]

        return ""

    def reinit_iotagent_with_ip(self, ip="", identifier="", headers={}, params={}):
        '''
        simulate to reinti iotagent
        send register to iot manager

        :param ip:  ip for the iotagent
        :param identifier:  for iotagent
        :return:  True if ok
        '''

        json = {"protocol": "PDI-IoTA-UltraLight", "description": "UL2"}
        json["iotagent"] = ip
        json["identifier"] = identifier
        json["resource"] = "/iot/d"

        headers = self.compose_headers(headers)
        res = self.api_post("protocols", headers=headers, data=json)

        if (res.status_code == 201):
            return ""
        else:
            return res.content

    def set_token(self, token):
        self.token = token
