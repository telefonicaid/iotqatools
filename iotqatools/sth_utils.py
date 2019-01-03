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
__author__ = 'macs'

import json
import requests
from requests.exceptions import RequestException
from iotqatools.iot_logger import get_logger
from iotqatools.iot_tools import PqaTools


class SthUtils(object):
    """
    Basic functionality for STH
    """

    def __init__(self, instance, service=None, subservice=None,
                 protocol="http",
                 port="8666",
                 path_raw_data="/STH/v1/contextEntities",
                 path_version="/version",
                 log_instance=None,
                 log_verbosity='DEBUG',
                 default_headers={"Accept": "application/json"},
                 check_json=True,
                 verify=False,
                 path_notify="/notify"):
        """
        STH Utils constructor
        :param instance:
        :param service:
        :param subservice:
        :param protocol:
        :param port:
        :param path_raw_data:
        :param path_version:
        :param log_instance:
        :param log_verbosity:
        :param default_headers:
        :param check_json:
        :param verify:        
        :param path_notify:
        """
        # initialize logger
        if log_instance is not None:
            self.log = log_instance
        else:
            self.log = get_logger('SthUtils', log_verbosity)

        # Assign the values
        self.default_endpoint = protocol + '://' + instance + ':' + port
        self.headers = self.__set_headers(default_headers, service, subservice)
        self.path_raw_data = self.default_endpoint + path_raw_data
        self.path_version = path_version
        self.check_json = check_json
        self.verify = verify
        self.path_notify = path_notify

    def __send_request(self, method, url, headers=None, payload=None, verify=None, query=None):
        """
        Send a request to a specific url in a specifig type of http request
        """

        parameters = {
            'method': method,
            'url': url,
        }

        if headers is not None:
            parameters.update({'headers': headers})

        if payload is not None:
            if self.check_json:
                parameters.update({'data': json.dumps(payload)})
            else:
                parameters.update({'data': payload})

        if query is not None:
            parameters.update({'params': query})

        if verify is not None:
            parameters.update({'verify': verify})
        else:
            # If the method does not include the verify parameter, it takes the vale from object
            parameters.update({'verify': self.verify})

        # Send the requests
        try:
            response = requests.request(**parameters)
        except RequestException, e:
            PqaTools.log_requestAndResponse(url=url, headers=headers, data=payload, comp='STH', method=method)
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)

        # Log data
        PqaTools.log_fullRequest(comp='STH', response=response, params=parameters)

        return response

    def __set_headers(self, default_headers, service, subservice):
        """
        Function that set the service and subservice headers before sent. Add this headers to the defaults one
        :param service:
        :param subservice:
        :return:
        """
        headers = default_headers.copy()
        if service is not None:
            headers.update({'Fiware-Service': service})
        if subservice is not None:
            headers.update({'Fiware-Servicepath': subservice})
        return headers.copy()

    def set_service(self, service):
        self.headers['Fiware-Service'] = service

    def set_subservice(self, subservice):
        self.headers['Fiware-Servicepath'] = subservice

    def set_token(self, token):
        self.headers['x-auth-token'] = token

    def set_path(self, ent_type, ent_id, attribute):
        """
        Build the path. It can be a path for the whole service/servicepath, the entity or certain attribute
        :param ent_type: (optional)
        :param ent_id:   (optional except if attribute is passed as param)
        :param attribute: (optional)
        :return:
        """
        path_template = ''

        if ent_id is not None:
            path_template = '/type/{entity_type}/id/{entity_id}'
            if attribute is not None:
                path_template += '/attributes/{attrib}'
        elif attribute is not None:
            raise Exception("missing parameter ent_id")

        path = self.path_raw_data + path_template.format(
            entity_type=ent_type,
            entity_id=ent_id,
            attrib=attribute)

        return path

    def version(self):
        """
        Get STH version
        """
        url = self.default_endpoint + self.path_version

        # send the request for the subscription
        response = self.__send_request('get', url, self.headers)
        return response

    def statistics(self):
        """
        Get STH statistics
        """
        url = self.default_endpoint + self.path_statistics

        # send the request for the subscription
        response = self.__send_request('get', url, self.headers)
        return response

    def request_raw_data(self, ent_type, ent_id, attribute, hLimit=None, offset=None, date_from=None,
                         date_to=None, service=None, subservice=None, lastN=None, filetype=None, token=None):
        path = self.set_path(ent_type, ent_id, attribute)
        query = {'lastN': lastN, 'hLimit': hLimit, 'hOffset': offset,
                 'dateFrom': date_from, 'dateTo': date_to, 'filetype': filetype}
        if service is not None:
            self.set_service(service)
        if subservice is not None:
            self.set_subservice(subservice)
        self.set_token(token)
        self.log.debug("Path: {}. Params: {}".format(path, query))
        return self.__send_request(method='get', url=path, headers=self.headers, query=query, verify=False)

    def request_aggregated_data(self, ent_type, ent_id, attribute, aggrMethod, aggrPeriod, date_from, date_to,
                                service='', subservice='', token=None):
        path = self.set_path(ent_type, ent_id, attribute)
        query = {'aggrMethod': aggrMethod, 'aggrPeriod': aggrPeriod, 'dateFrom': date_from, 'dateTo': date_to}
        self.set_service(service)
        self.set_subservice(subservice)
        self.set_token(token)
        self.log.debug("Path: {}. Params: {}".format(path, query))
        return self.__send_request(method='get', url=path, headers=self.headers, query=query, verify=False)

    def send_notification(self, payload, service=None, subservice=None, token=None):
        """
        notify STH new values
        """
        url = self.default_endpoint + self.path_notify
        if service is not None:
            self.set_service(service)
        if subservice is not None:
            self.set_subservice(subservice)
        self.set_token(token)
        self.headers.update({'content-type': 'application/json'})
        self.log.debug("Path: {}. Headers: {}".format(url, self.headers))
        return self.__send_request(method='post', url=url, headers=self.headers, payload=payload, verify=False)

    def delete(self, ent_type=None, ent_id=None, attribute=None, service=None, subservice=None, token=None):
        """
        Deletes all the data stored in STH related to the query formed by params
        Queries:
        * Delete all the data associated to certain attribute of certain entity of certain service and servicepath
        * Delete all the data associated to certain entity of certain service and servicepath
        * Delete all the data associated to certain service and servicepath
        """

        if service is not None:
            self.set_service(service)
        if subservice is not None:
            self.set_subservice(subservice)
        self.set_token(token)
        path = self.set_path(ent_type, ent_id, attribute)
        return self.__send_request(method='delete', url=path, headers=self.headers, verify=False)

