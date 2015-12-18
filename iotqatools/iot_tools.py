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

import re
import ast
import pprint
import json
from iotqatools.iot_logger import get_logger


class PqaTools(object):
    """
    PqaTools:   Test tools to store retrieve and print info during the tests
    >>> dir(PqaTools)
    ['dict_pattern_recall', 'dict_recall', 'get_attribute', 'log_result',
    'log_requestAndResponse','pattern_mapping', 'pattern_recall', 'pm',
    'recall', 'remember', 'replace', 'secure_headers']
    """

    @staticmethod
    def log_requestAndResponse(url='', headers={}, params={}, data='', comp='', response={}, method=''):
        """
        Print the result of a request and the response data provided in a standard view
        :param url: Endpoint where the request was sent
        :param headers: Headers sent to the component (if any)
        :param params: Params sent to the component (if any)
        :param data: Data sent to the component (if any)
        :param comp: IoT component under test (optional)
        :param response: response of a request (optional)
        :param method: http method, it can be POST, GET, PUT, DELETE (optional)
        :return: Nan
        """
        log = get_logger('iot_tools')

        log_msg = '>>>>>>>>>>>>>\t Data sent:     \t>>>>>>>>>>>>> \n'
        if comp:
            log_msg += "\t> Comp: {} \n".format(comp)
        if method:
            log_msg += "\t> Method: {} \n".format(method)
        if url:
            log_msg += "\t> Url: {} \n".format(url)
        if headers:
            log_msg += '\t> Headers: {}\n'.format(str(dict(headers)))
            # log_msg += "\t> Headers: {} \n".format(pprint.pformat(headers, width=20))
        if params:
            log_msg += "\t> Params: {} \n".format(pprint.pformat(params, width=20))
        if data is not '':
            log_msg += "\t> Payload sent: {}\n".format(pprint.pformat(data, width=20))
        else:
            log_msg += "\t> SENT REQUEST DATA SEEMS TO BE EMPTY \n"
        log.debug(log_msg)

        if response:
            log_msg = '<<<<<<<<<<<<<<\t Data responded:\t<<<<<<<<<<<<<<\n'
            if isinstance(response, object) and hasattr(response, "status_code"):
                log_msg += '\t< Response code: {}\n'.format(str(response.status_code))
            log_msg += '\t< Headers: {}\n'.format(str(dict(response.headers)))
            try:
                if response.content:
                    log_msg += '\t< Payload received: {}\n'.format(response.content)
                else:
                    log_msg += '\t< Empty Payload \n'
            except ValueError:
                log_msg += '\t< Payload received:\n %s' % response.content

        # Log responded data
        log.debug(log_msg)

    @staticmethod
    def log_result(url='', headers={}, params={}, data='', comp='', method=''):
        """
        Just print the request and the response stored in world[IotComponent].response (if any)
        :param url: Endpoint where the request was sent
        :param headers: Headers sent to the component (if any)
        :param params: Params sent to the component (if any)
        :param data: Data sent to the component (if any)
        :param comp: IoT component under test (needed to recover the data)
        :param method: http method  (POST, GET, PUT, DELETE)
        :return: Nan
        """
        PqaTools.log_requestAndResponse(url=url, headers=headers, params=params,
                                        data=data, comp=comp, method=method)

    @staticmethod
    def log_fullRequest(comp='', response='', params=dict()):
        # initialize logger
        log = get_logger('iot_tools')

        # Introduce info in log text
        log_msg = '>>>>>>>>>>>>>\t Data sent:     \t>>>>>>>>>>>>> \n'
        if 'comp' is not '':
            log_msg += '\t> Comp: %s\n' % comp
        if 'url' in params:
            log_msg += '\t> Url: %s\n' % params['url']
        if 'method' in params:
            log_msg += '\t> Method: %s\n' % params['method']
        if 'headers' in params:
            log_msg += '\t> Headers: {}\n'.format(str(params['headers']))
        if 'data' in params:
            log_msg += '\t> Payload sent: {}\n'.format(pprint.pformat(params['data'], width=20))
        if 'query' in params:
            log_msg += '\t> Query: %s\n' % params['query']
        if 'verify' in params:
            log_msg += '\t> Verify: %s\n' % params['verify']

        # Log sent data
        log.debug(log_msg)

        log_msg = '<<<<<<<<<<<<<<\t Data responded:\t<<<<<<<<<<<<<<\n'
        log_msg += '\t< Response code: {}\n'.format(str(response.status_code))
        log_msg += '\t< Headers: {}\n'.format(str(dict(response.headers)))
        try:
            log_msg += '\t< Payload received:\n {}'.format(response.content)
        except ValueError:
            log_msg += '\t< Payload received:\n %s' % response.content.text

        # Log responded data
        log.debug(log_msg)

        return 0

    @staticmethod
    def pattern_mapping(cad, mapping):
        """
        Fill the template with all the values available in world
        cad: chain with <%patterns%>
        mapping: dictionary with substitutions
        """
        for it in mapping:
            if isinstance(mapping[it], str) or isinstance(mapping[it], unicode):
                # Only try with content 'str' or 'unicode'
                cad = re.sub('<%' + it + '%>', mapping[it], cad)
        return cad

    @staticmethod
    def remember(place, key, value):
        """The 'selection' parameters management """
        log = get_logger('iot_tools')
        place[key] = value
        log.debug("#>> {0} AS {1} in {2}".format(value, key, place))

    @staticmethod
    def recall(cad, place):
        """Mapping of a cad from world.g -remembered data-"""
        return PqaTools.pattern_mapping(cad, place)

    @staticmethod
    def pattern_recall(comp, pattern, place):
        """Mapping of world.c[comp][pattern] from dict -remembered data-"""
        return PqaTools.recall(place[comp][pattern], place)

    @staticmethod
    def dict_recall(cad, place):
        """Mapping of a cad from world.g -remembered data-, but transformed into a dict"""
        return ast.literal_eval(PqaTools.recall(cad, place))

    @staticmethod
    def dict_pattern_recall(comp, pattern, place):
        """Mapping of world.c[comp][pattern] from world.g -remembered data-, but transformed into a dict"""
        return PqaTools.dict_recall(place[comp][pattern])

    @staticmethod
    def get_attribute(attr, data):
        """
        Obtain a field from a json
        """
        jsobject = json.loads(data)
        return jsobject[attr]
