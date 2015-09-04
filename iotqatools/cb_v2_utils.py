# -*- coding: utf-8 -*-
"""
Copyright 2015 Telefonica Investigación y Desarrollo, S.A.U

This file is part of telefonica-iot-qa-tools

orchestrator is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

orchestrator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with orchestrator.
If not, seehttp://www.gnu.org/licenses/.

For those usages not covered by the GNU Affero General Public License
please contact with::[iot_support@tid.es]
"""

__author__ = 'Iván Arias León (ivan dot ariasleon at telefonica dot com)'

import requests

from helpers_utils import *


# general constants
EMPTY = u''
TRUE = u'true'
FALSE = u'false'
JSON = u'JSON'
PARAMETER = u'parameter'
VALUE = u'value'
RANDOM = u'random'

# requests constants
VERSION = u'version'
ORION = u'orion'
V2_ENTITIES = u'v2/entities'

MAX_LENGTH_ALLOWED = u'max length allowed'
GREATER_THAN_MAX_LENGTH_ALLOWED = u'greater than max length allowed'
MAX_LENGTH_ALLOWED_AND_TEN_LEVELS = u'max length allowed and ten levels'
GREATER_THAN_MAX_LENGTH_ALLOWED_AND_TEN_LEVELS = u'greater than max length allowed and ten levels'
MAX_LENGTH_ALLOWED_AND_ELEVEN_LEVELS = u'max length allowed and eleven levels'
CHARS_ALLOWED = string.ascii_letters + string.digits + u'_'     # regular expression: [a-zA-Z0-9_]+
SERVICE_MAX_CHARS_ALLOWED = 50
SERVICE_PATH_LEVELS = 10
FIWARE_SERVICE = u'Fiware-Service'
FIWARE_SERVICE_PATH = u'Fiware-ServicePath'

__logger__ = logging.getLogger("utils")


class CB:
    """
    manage Context broker operations
    """
    def __init__(self,  **kwargs):
        """
        constructor
        :param protocol: protocol used in context broker requests
        :param host: host used by context broker
        :param port: port used by context broker
        """
        self.cb_protocol = kwargs.get("protocol", "http")
        self.cb_host = kwargs.get("host", "localhost")
        self.cb_port = kwargs.get("port", "1026")

        self.cb_url = "%s://%s:%s" % (self.cb_protocol, self.cb_host, self.cb_port)
        self.headers = {}
        self.entity_context = {"entities_number": None,
                               "entities_type": None,            # entity type prefix.
                               "entities_id": None,              # entity id prefix.
                               "attributes_number": None,
                               "attributes_name": None,
                               "attributes_value": None,
                               "attributes_type": None,
                               "metadatas_number": None,
                               "metadatas_name": None,
                               "metadatas_type": None,
                               "metadatas_value": None}
        self.entities_parameters = {}

    # ------------------------------------ requests --------------------------------------------
    def get_version_request(self):
        """
        get the context broker version
        :return response to an HTTP request
        """
        header = {"Accept": "application/json"}
        resp = self.__send_request("GET", VERSION, headers=header)

        assert resp.status_code == 200, " ERROR - status code in context broker version request. \n " \
                                        " status code: %s \n " \
                                        " body: %s" % (resp.status_code, resp.text)
        __logger__.info(" -- status code is 200 OK in version request")
        return resp

    def get_statistics_request(self):
        """
        get context broker statistics
        :return response to an HTTP request
        """
        header = {"Accept": "application/json"}
        resp = self.__send_request("GET", "statistics", headers=header)

        assert resp.status_code == 200, " ERROR - status code in context broker statistics request. \n " \
                                        " status code: %s \n " \
                                        " body: %s" % (resp.status_code, resp.text)
        __logger__.info(" -- status code is 200 OK in statistics request")
        return resp

    def get_base_request(self):
        """
        get a API entry point request
        :return response to an HTTP request
        """
        header = {"Accept": "application/json"}
        resp = self.__send_request("GET", "v2", headers=header)

        assert resp.status_code == 200, " ERROR - status code in context broker base request. \n" \
                                        " status code: %s \n " \
                                        " body: %s" % (resp.status_code, resp.text)
        __logger__.info(" -- status code is 200 OK in API entry point request v2")
        return resp

    @staticmethod
    def __generate_service_path(length, levels=1):
        """
        generate random service path header with several levels
        :param levels: maximum scope levels in a path
        :param length: maximum characters in each level
        :return: service path (string)
        """
        temp = EMPTY
        for i in range(levels):
            temp = "%s/%s" % (temp,  string_generator(length, CHARS_ALLOWED))
        return temp

    def definition_headers(self, context):
        """
        definition of headers ex: {"Fiware-Service": "happy_path", "Fiware-ServicePath": "/test"}
           | parameter          | value      |
           | Fiware-Service     | happy_path |
           | Fiware-ServicePath | /test      |
        Hint: if value is "max length allowed", per example, it is random value with max length allowed and characters allowed
        :param context: context variable
        """
        for row in context.table:
            self.headers[row[PARAMETER]] = row[VALUE]

        if FIWARE_SERVICE in self.headers:
            if self.headers[FIWARE_SERVICE] == MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE] = string_generator(SERVICE_MAX_CHARS_ALLOWED, CHARS_ALLOWED)
            elif self.headers[FIWARE_SERVICE] == GREATER_THAN_MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE] = string_generator(SERVICE_MAX_CHARS_ALLOWED+1, CHARS_ALLOWED)

        if FIWARE_SERVICE_PATH in self.headers:
            if self.headers[FIWARE_SERVICE_PATH] == MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED)
            elif self.headers[FIWARE_SERVICE_PATH] == GREATER_THAN_MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED+1)
            elif self.headers[FIWARE_SERVICE_PATH] == MAX_LENGTH_ALLOWED_AND_TEN_LEVELS:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED, SERVICE_PATH_LEVELS)
            elif self.headers[FIWARE_SERVICE_PATH] == GREATER_THAN_MAX_LENGTH_ALLOWED_AND_TEN_LEVELS:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED+1, SERVICE_PATH_LEVELS)
            elif self.headers[FIWARE_SERVICE_PATH] == MAX_LENGTH_ALLOWED_AND_ELEVEN_LEVELS:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED, SERVICE_PATH_LEVELS+1)
        __logger__.debug("Headers: %s" % str(self.headers))

    @staticmethod
    def __create_metadata(metadata_number, metadata_name, metadata_type, metadata_value):
        """
        create N metadatas dynamically. The value could be random value ("random").
        :param metadata_number: number of metadatas
        :param metadata_name: name of metadatas eit a prefix plus a consecutive value
        :param metadata_value: metadatas value. It could be random value ("random")
        - with type:
            "metadata_name": {"value": "metadata_value",
                              "type": "metadata_type" }
        - without type:
             "metadata_name": "metadata_value"
        :return metadatas dict
        """
        meta_dict = {}
        meta_type = {}
        value = metadata_value
        for i in range(int(metadata_number)):
            if metadata_value == RANDOM:
                value = string_generator(5)
            if metadata_type is None:
                meta_dict["%s_%s" % (metadata_name, str(i))] = value
            else:
                meta_type["value"] = value
                meta_type["type"] = metadata_type
                meta_dict["%s_%s" % (metadata_name, str(i))] = meta_type
        return meta_dict

    @staticmethod
    def __get_random_number(label):
        """
        get random number
        :param label: ex: random=10 return: 10
        :return int
        """
        return int(label.split("=")[1])

    def __send_request(self, method, path, **kwargs):
        """
        send a request to context broker server
        :param method: http method (POST, GET, etc)
        :param path: url path (ex: /v2/entities)
        :param payload: json body
        :param show: is used to display request and response if they are necessary
        :return http response
        """
        headers = kwargs.get("headers", None)
        payload = kwargs.get("payload", None)
        show = kwargs.get("show", True)
        parameters = kwargs.get("parameters", None)
        if show:
            __logger__.debug("----------------- Request ---------------------------------")
            p = EMPTY
            if parameters is not None and parameters != {}:
                for item in parameters:
                    p = '%s&%s=%s' % (p, item, parameters[item])
                p_t = list(p)
                p_t[0] = "?"
                p = "".join(p_t)
            __logger__.debug("url: %s %s/%s%s" % (method, self.cb_url, path, p))
            if headers is not None:
                __logger__.debug("headers:")
                for item in headers:
                    __logger__.debug("   %s: %s" % (item, headers[item]))
            if payload is not None:
                __logger__.debug("payload: %s" % payload)
                __logger__.debug("payload length: %s" % str(len(payload)))
            __logger__.debug("-------------------------------------------------------------------------")
        resp = requests.request(method=method,
                                url="%s/%s" % (self.cb_url, path),
                                headers=headers,
                                data=payload,
                                params=parameters)
        if show:
            __logger__.debug("----------------- Response ---------------------------------")
            __logger__.debug(" http code: %s" % (resp.status_code))
            __logger__.debug(" body: %s" % (resp.text))
            __logger__.debug("-------------------------------------------------------------------------")
        return resp

    def create_entities(self, context, entities_number, attributes_number):
        """
        create N entities with N properties and another optional parameters:
          -  entity_type, entity_id, attributes_name, attributes_value, attribute_type, metadata_name and metadata_value
                Example:
                      | parameter   | value                   |
                      | entity_type | room                    |
                      | entity_id   | room2                   |
                      | attr_name   | timestamp               |
                      | attr_value  | 017-06-17T07:21:24.238Z |
                      | attr_type   | date                    |
                      | meta_number | 1                       |
                      | meta_name   | very_hot                |
                      | meta_type   | alarm                   |
                      | meta_value  | false                   |
        :param context: context variable (optional parameters)
        :param entities_number: number of entities
        :param attributes_number: number of attributes
        Hints:
            - "attr_name", "attr_value", "attr_type", "meta_name", "meta_type" and "meta_value" could be random values.
              The number after "=" is the number of chars
                ex: | attr_name | random=10 |
            - If attribute number is "1", the attribute name is without consecutive, ex: attribute_name=temperature.
              Else attributes number is major than "1" the attributes name are prefix plus consecutive, ex:
                 attributes_name=temperature_1,...,temperature_N (see "atribute name with consecutive or not" comment)
        :return responses list
        """
        attributes = {}
        resp_list = []
        entities = {}
        self.entity_context["entities_number"] = int(entities_number)
        self.entity_context["attributes_number"] = int(attributes_number)

        # store parameters in entities contexts
        if context.table is not None:
            for row in context.table:
                if row[PARAMETER] in self.entity_context:
                    self.entity_context[row[PARAMETER]] = row[VALUE]
                else:
                    __logger__.debug("Wrong parameter: %s" % row[PARAMETER])

        # Random values
        random_labels = ["attributes_name", "attributes_value", "attributes_type", "metadatas_name", "metadatas_value", "metadatas_type"]
        for random_label in self.entity_context:
            if random_label in random_labels:
                if (self.entity_context[random_label] is not None) and (self.entity_context[random_label].find(RANDOM) >= 0):
                    self.entity_context[random_label] = string_generator(self.__get_random_number(self.entity_context[random_label]))

        # log entities contexts
        for item in self.entity_context:
            __logger__.debug("%s: %s" % (item, self.entity_context[item]))

        # append attribute type, attribute metadatas and attribute value if the first two exist for one attribute
        if self.entity_context["metadatas_number"] is not None:
            attributes = self.__create_metadata(self.entity_context["metadatas_number"],
                                                self.entity_context["metadatas_name"],
                                                self.entity_context["metadatas_type"],
                                                self.entity_context["metadatas_value"])
        __logger__.debug("Metadatas: %s" % str(attributes))
        if self.entity_context["attributes_type"] is not None:
            attributes["type"] = self.entity_context["attributes_type"]
        if self.entity_context["attributes_value"] is not None and attributes != {}:
            attributes["value"] = self.entity_context["attributes_value"]
        __logger__.debug("Attributes: %s" % str(attributes))

        # append N attributes with previous config or not
        if self.entity_context["attributes_name"] is not None:
            for i in range(self.entity_context["attributes_number"]):
                # atribute name with consecutive or not
                if self.entity_context["attributes_number"] == 1:
                    name = self.entity_context["attributes_name"]
                else:
                    name = "%s_%s" % (self.entity_context["attributes_name"], str(i))
                if attributes == {}:
                    entities[name] = self.entity_context["attributes_value"]
                else:
                    entities[name] = attributes

        # create N consecutive entities with previous N attributes
        for e in range(self.entity_context["entities_number"]):
            if self.entity_context["entities_type"] is not None:
                entities["type"] = self.entity_context["entities_type"]
            if self.entity_context["entities_id"] is not None:
                entities["id"] = "%s_%s" % (self.entity_context["entities_id"], str(e))
            payload = convert_dict_to_str(entities, "JSON")
            resp_list.append(self.__send_request("POST", V2_ENTITIES, headers=self.headers, payload=payload))

        return resp_list

    def create_entity_raw(self, context):
        """
        create an entity with raw value per special cases (compound, vector, boolean, integer, etc):
            ex:
                 "value": true
                 "value": false
                 "value": 34
                 "value": 5.00002
                 "value": [ "json", "vector", "of", 6, "strings", "and", 2, "integers" ]
                 "value": {"x": {"x1": "a","x2": "b"}}
                 "value": "41.3763726, 2.1864475,14"  -->  "type": "geo:point"
                 "value": "2017-06-17T07:21:24.238Z"  -->  "type: "date"
        Some cases are not parsed correctly to dict in python
        """
        entity = EMPTY
        metadata = EMPTY
        attribute_str = EMPTY
        if context.table is not None:
            for row in context.table:
                if row[PARAMETER] in self.entity_context:
                    self.entity_context[row[PARAMETER]] = row[VALUE]
                else:
                    __logger__.debug("Wrong parameter: %s" % row[PARAMETER])
        self.entity_context["entities_number"] = 1
        self.entity_context["attributes_number"] = 1

        # log entities contexts
        for item in self.entity_context:
            __logger__.debug("%s: %s" % (item, self.entity_context[item]))

        # create attribute with/without attribute type and metadatas (with/without type)
        if self.entity_context["attributes_type"] is not None:
            attribute_str = '"type": %s' % self.entity_context["attributes_type"]

        if self.entity_context["metadatas_name"] is not None:
            if self.entity_context["metadatas_type"] is not None:
                metadata = '%s: {"type": %s, "value": %s}' % (self.entity_context["metadatas_name"],
                                                                self.entity_context["metadatas_type"],
                                                                self.entity_context["metadatas_value"])
            else:
                metadata = '%s: %s' % (self.entity_context["metadatas_name"], self.entity_context["metadatas_value"])
            if attribute_str != EMPTY:
                attribute_str = '%s, %s' % (attribute_str, metadata)
            else:
                attribute_str = metadata

        #append attribute value in string format
        if attribute_str == EMPTY:
            attribute_str = '%s: %s' % (self.entity_context["attributes_name"], self.entity_context["attributes_value"])
        else:
            attribute_str = '%s: {%s, "value": %s}' % (self.entity_context["attributes_name"], attribute_str, self.entity_context["attributes_value"])
        __logger__.debug("Atribute: %s" % attribute_str)

        #create entity with attribute value in raw
        entity = u'{"type": %s, "id": %s, %s}' % (self.entity_context["entities_type"], self.entity_context["entities_id"], attribute_str)

        resp = self.__send_request("POST", V2_ENTITIES, headers=self.headers, payload=entity)
        return resp

    def list_all_entities(self, context):
        """
        list all entities
        | parameter | value                 |  (Optionals)
        | limit     | 2                     | Limit the number of entities to be retrieved
        | offset    | 3                     | Skip a number of records
        | id        | room_2, speed_3       | Id list
        | idPattern | room_*                | Id pattern
        | type      | room, vehicle         | Type list
        | q         | statement;statements  | There are two kind of statements: unary statements and binary staments.
        | geometry  | circle;radius:4000    | The first token is the shape of the geometry, the rest of the tokens (if any) depends on the shape
        | coords    | 41.3763726, 2.1864475 | List of coordinates (separated by ;)
        | attrs     | temperature           | Comma-separated list of attribute names
        | options   | count                 | The total number of entities is returned (X-Total-Count)
        | options   | canonical             | The response payload uses the "canonical form"
        :return: http response list
        """
        __logger__.info("List all entities, filtered by the queries parameters")
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        # log queries parameters
        for item in self.entities_parameters:
            __logger__.debug("Queries parameters: %s=%s" % (item, self.entities_parameters[item]))

        resp = self.__send_request("GET", V2_ENTITIES, headers=self.headers, parameters=self.entities_parameters)
        return resp

    def get_entity_context(self):
        """
        get entities contexts
        :return dict (see "constructor" method by dict fields)
        """
        return self.entity_context

    def get_headers(self):
        """
        return headers
            {
                "Fiware-Service": "service",
                "Fiware-ServicePath": "/service_path'
            }
        :return: dict (see "definition_headers" method by dict fields)
        """
        return self.headers

    def get_entities_parameters(self):
        """
        return queries parameters used in list entities
        :return: dict
        """
        return self.entities_parameters