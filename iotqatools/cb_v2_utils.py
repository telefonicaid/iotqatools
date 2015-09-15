# -*- coding: utf-8 -*-
"""
(c) Copyright 2015 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
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
RANDOM_ENTITIES_LABEL = ["attributes_name", "attributes_value", "attributes_type", "metadatas_name", "metadatas_value", "metadatas_type"]
RANDOM_QUERIES_PARAMETERS_LABELS = ["op"]

__logger__ = logging.getLogger("utils")


class CB:
    """
    manage Context broker operations
    """

    def __init_entity_context_dict(self):
        """
        initialize entity_context dict (used in create, update or append entity)
        """
        self.entity_context = {"entities_number": 1,
                               "entities_type": None,            # entity type prefix.
                               "entities_id": None,              # entity id prefix.
                               "attributes_number": 0,
                               "attributes_name": None,
                               "attributes_value": None,
                               "attributes_type": None,
                               "metadatas_number": 0,
                               "metadatas_name": None,
                               "metadatas_type": None,
                               "metadatas_value": None}

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
        self.__init_entity_context_dict()
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
        __logger__.info(" -- status code is 200 OK in API entry point request")
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
        name = EMPTY
        value = metadata_value
        for i in range(int(metadata_number)):
            if metadata_value == RANDOM:
                value = string_generator(5)
            if metadata_name != EMPTY:
                name = "%s_%s" % (metadata_name, str(i))
            if metadata_type is None:
                meta_dict[name] = value
            else:
                if value is not None:
                    meta_type["value"] = value
                meta_type["type"] = metadata_type
                meta_dict[name] = meta_type
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
            __logger__.debug(" headers:")
            for h in resp.headers:
                __logger__.debug("     %s: %s" % (h, resp.headers[h]))
            __logger__.debug(" body: %s " % resp.text)
            __logger__.debug("-------------------------------------------------------------------------")
        return resp

    def __random_values(self, random_labels, dictionary):
        """
        generate a random string if a label in a dict has "random=xxx" value
        "attr_name", "attr_value", "attr_type", "meta_name", "meta_type" and "meta_value" could be random values in entities
        "op" could be random values in queries parameters
              The number after of "=" is the number of random chars
        :param random_labels: labels to verify
        :param dictionary: dictionary with key-values
        :return (string) random
        """
        for random_label in dictionary:
            if random_label in random_labels:
                if (dictionary[random_label] is not None) and (dictionary[random_label].find(RANDOM) >= 0):
                    dictionary[random_label] = string_generator(self.__get_random_number(dictionary[random_label]))
        return dictionary

    def __create_attributes(self, entity_context):
        """
        create attributes with entity context
        :return (dict) attribute list
        """
        attributes = {}
        entities = {}
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
            for i in range(int(self.entity_context["attributes_number"])):
                # atribute name with consecutive or not
                if self.entity_context["attributes_number"] == 1:
                    name = self.entity_context["attributes_name"]
                else:
                    name = "%s_%s" % (self.entity_context["attributes_name"], str(i))
                if attributes == {}:
                    entities[name] = self.entity_context["attributes_value"]
                else:
                    entities[name] = attributes
        return entities

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
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)

        # log entities contexts
        for item in self.entity_context:
            __logger__.debug("%s: %s" % (item, self.entity_context[item]))

        # create attributes with entity context
        entities = self.__create_attributes(self.entity_context)

        # create N consecutive entities with previous N attributes
        for e in range(self.entity_context["entities_number"]):
            if self.entity_context["entities_type"] is not None:
                entities["type"] = self.entity_context["entities_type"]
            if self.entity_context["entities_id"] is not None:
                if self.entity_context["entities_number"] == 1:
                    entities["id"] = self.entity_context["entities_id"]
                else:
                    entities["id"] = "%s_%s" % (self.entity_context["entities_id"], str(e))

            payload = convert_dict_to_str(entities, "JSON")
            if entities != {}:
                resp_list.append(self.__send_request("POST", V2_ENTITIES, headers=self.headers, payload=payload))
            else:
                resp_list.append(self.__send_request("POST", V2_ENTITIES, headers=self.headers))
        return resp_list

    def __create_attribute_raw(self,entity_context):
        """
        create an attribute with entity context in raw mode
        :return (string)
        """
        attribute_str = EMPTY
        # create attribute with/without attribute type and metadatas (with/without type)
        if entity_context["attributes_type"] is not None:
            attribute_str = '"type": %s' % self.entity_context["attributes_type"]

        if entity_context["metadatas_name"] is not None:
            if entity_context["metadatas_type"] is not None:
                metadata = '%s: {"type": %s, "value": %s}' % (entity_context["metadatas_name"],
                                                              entity_context["metadatas_type"],
                                                              entity_context["metadatas_value"])
            else:
                metadata = '%s: %s' % (entity_context["metadatas_name"], entity_context["metadatas_value"])
            if attribute_str != EMPTY:
                attribute_str = '%s, %s' % (attribute_str, metadata)
            else:
                attribute_str = metadata

        #append attribute value in string format
        if attribute_str == EMPTY:
            attribute_str = '%s: %s' % (entity_context["attributes_name"], entity_context["attributes_value"])
        else:
            if entity_context["attributes_value"] is not None:
                attribute_str = '%s: {%s, "value": %s}' % (entity_context["attributes_name"], attribute_str, entity_context["attributes_value"])
            else:
                attribute_str = '%s: {%s}' % (entity_context["attributes_name"], attribute_str)
        __logger__.debug("Atribute: %s" % attribute_str)
        return attribute_str


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
        attribute_str = self.__create_attribute_raw(self.entity_context)

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

    def list_an_entity_by_ID(self, context, entity_id):
        """
        get an entity by ID
          | parameter | value       |
          | attrs     | temperature |
        Hint: if we need " char, use \' and it will be replaced (mappping_quotes)
        :return: http response
        """
        self.entity_id_to_request = mapping_quotes(entity_id) # used to verify if the entity returned is the expected
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        # log queries parameters
        __logger__.debug("entity_id: %s" % self.entity_id_to_request)
        for item in self.entities_parameters:
            __logger__.debug("Queries parameters: %s=%s" % (item, self.entities_parameters[item]))

        resp = self.__send_request("GET", "%s/%s" % (V2_ENTITIES, self.entity_id_to_request), headers=self.headers,
                                   parameters=self.entities_parameters)
        return resp

    def list_an_attribute_by_ID(self, attribute_name, entity_id):
        """
        get an attribute by ID
        """
        self.entity_id_to_request = mapping_quotes(entity_id) # used to verify if the entity returned is the expected
        self.attribute_name_to_request = mapping_quotes(attribute_name) # used to verify if the attribute returned is the expected
        # log messages
        __logger__.debug("entity_id: %s" % self.entity_id_to_request)
        __logger__.debug("attribute_name: %s" % self.attribute_name_to_request)

        resp = self.__send_request("GET", "%s/%s/attrs/%s" % (V2_ENTITIES, self.entity_id_to_request, self.attribute_name_to_request),
                                   headers=self.headers, parameters=self.entities_parameters)
        return resp

    def update_or_append_an_attribute_by_id(self, context, entity_id):
        """
        update or append an attribute by id
        :param context: new values to update or append
        :param entity_id: entity used to update or append
        Hint: if would like a wrong query parameter name, use `qp_` prefix
        :return http response
        """
        self.entity_id_to_request = mapping_quotes(entity_id) # used to verify if the entity returned is the expected
        self.__init_entity_context_dict()
        if context.table is not None:
            for row in context.table:
                __logger__.debug("parameters:  %s = %s" % (row[PARAMETER], row[VALUE]))
                if row[PARAMETER] in self.entity_context:
                    self.entity_context[row[PARAMETER]] = row[VALUE]
                elif row[PARAMETER] == "op":
                    self.entities_parameters[row[PARAMETER]] = row[VALUE]
                elif row[PARAMETER].find("qp_") >= 0:
                    __logger__.debug("pepe: %s" % row[PARAMETER])
                    __logger__.debug("pepe type: %s" % str(type(row[PARAMETER])))
                    qp = str(row[PARAMETER]).split("qp_")[1]
                    __logger__.debug("pepe: %s" % str(qp))
                    self.entities_parameters[qp] = row[VALUE]

            self.entity_context["entities_id"] = entity_id
            if  self.entity_context["attributes_number"] == 0 and self.entity_context["attributes_name"] is not None:
                self.entity_context["attributes_number"] = 1
            if  self.entity_context["metadatas_number"] == 0 and self.entity_context["metadatas_name"] is not None:
                self.entity_context["metadatas_number"] = 1

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)
        self.entities_parameters = self.__random_values(RANDOM_QUERIES_PARAMETERS_LABELS, self.entities_parameters)

        # log entities contexts
        __logger__.debug("entity context to update or append")
        for item in self.entity_context:
            __logger__.debug("%s: %s" % (item, self.entity_context[item]))

        # log entities_parameters
        __logger__.debug("queries parameters to update or append")
        for item in self.entities_parameters:
            __logger__.debug("%s: %s" % (item, self.entities_parameters[item]))

        # create attributes with entity context
        entities = self.__create_attributes(self.entity_context)

        payload = convert_dict_to_str(entities, "JSON")
        if entities != {}:
            resp = self.__send_request("POST", "%s/%s" % (V2_ENTITIES, entity_id), headers=self.headers, payload=payload,
                                   parameters=self.entities_parameters)
        else:
            resp = self.__send_request("POST", "%s/%s" % (V2_ENTITIES, entity_id), headers=self.headers,
                                   parameters=self.entities_parameters)

        return resp

    def update_or_append_an_attribute_in_raw_by_id(self, context, entity_id):
        """
        update or append an entity with raw value per special cases (compound, vector, boolean, integer, etc):
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
        self.__init_entity_context_dict()
        entity = EMPTY
        metadata = EMPTY
        attribute_str = EMPTY
        if context.table is not None:
            for row in context.table:
                if row[PARAMETER] in self.entity_context:
                    self.entity_context[row[PARAMETER]] = row[VALUE]
                elif row[PARAMETER] == "op":
                    self.entities_parameters[row[PARAMETER]] = row[VALUE]
                else:
                    __logger__.debug("Wrong parameter: %s" % row[PARAMETER])
        self.entity_context["entities_number"] = 1
        self.entity_context["attributes_number"] = 1

        # log entities contexts
        for item in self.entity_context:
            __logger__.debug("%s: %s" % (item, self.entity_context[item]))

        # create attribute with/without attribute type and metadatas (with/without type)
        attribute_str = "{%s}" % self.__create_attribute_raw(self.entity_context)

        resp = self.__send_request("POST", "%s/%s" % (V2_ENTITIES, entity_id),
                                   headers=self.headers, payload=attribute_str,
                                   parameters=self.entities_parameters)
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

    def get_entity_id_to_request(self):
        """
        return entity id used in request to get an entity
        used to verify if the entity returned is the expected
        :return string
        """
        return self.entity_id_to_request

    def get_attribute_name_to_request(self):
        """
        return attribute name used in request to get an attribute
        used to verify if the attribute returned is the expected
        :return string
        """
        return self.attribute_name_to_request
    
		
