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
__author__ = 'Iván Arias León (ivan dot ariasleon at telefonica dot com)'

import requests
import socket

from helpers_utils import *


# general constants
EMPTY = u''
TRUE = u'true'
FALSE = u'false'
JSON = u'JSON'
NONE = u'none'   # used as default value in type, attr_type and metadata_type
PARAMETER = u'parameter'
VALUE = u'value'
TYPE = u'type'
METADATA = u'metadata'
RANDOM = u'random'
ENTITY = u'entity'
PREFIX = u'prefix'
ID = u'id'
IDPATTERN = u'idPattern'

# requests constants
VERSION = u'version'
ORION = u'orion'
V2_ENTITIES = u'v2/entities'
V2_SUBSCRIPTIONS = u'v2/subscriptions'
V2_TYPES = u'v2/types'
GET = u'GET'
POST = u'POST'
PUT = u'PUT'
DELETE = u'DELETE'
NORMALIZED = u'normalized'
KEY_VALUES = u'keyValues'

# queries parameters
OPTIONS = u'options'

# entity context dict
ENTITIES_NUMBER = u'entities_number'
ENTITIES_TYPE = u'entities_type'
ENTITIES_ID = u'entities_id'
ENTITIES_PREFIX = u'entities_prefix'
ATTRIBUTES_NUMBER = u'attributes_number'
ATTRIBUTES_NAME = u'attributes_name'
ATTRIBUTES_VALUE = u'attributes_value'
ATTRIBUTES_TYPE = u'attributes_type'
METADATAS_NUMBER = u'metadatas_number'
METADATAS_NAME = u'metadatas_name'
METADATAS_TYPE = u'metadatas_type'
METADATAS_VALUE = u'metadatas_value'

# description context dict
DESCRIPTION = u'description'
SUBJECT_TYPE= u'subject_type'
SUBJECT_ID= u'subject_id'
SUBJECT_IDPATTERN= u'subject_idPattern'
SUBJECT_ENTITIES_NUMBER= u'subject_entities_number'
SUBJECT_ENTITIES_PREFIX= u'subject_entities_prefix'
CONDITION_ATTRS = u'condition_attrs'
CONDITION_ATTRS_NUMBER = u'condition_attrs_number'
CONDITION_EXPRESSION = u'condition_expression'
NOTIFICATION_ATTRS = u'notification_attrs'
NOTIFICATION_ATTRS_NUMBER = u'notification_attrs_number'
NOTIFICATION_ATTRSFORMAT = u'notification_attrsFormat'
NOTIFICATION_HTTP_URL = u'notification_http_url'
NOTIFICATION_HTTP_HEADERS = u'notification_http_headers'
NOTIFICATION_HTTP_QS = u'notification_http_qs'
NOTIFICATION_HTTP_METHOD = u'notification_http_method'
NOTIFICATION_HTTP_PAYLOAD = u'notification_http_payload'
THROTTLING = u'throttling'
EXPIRES = u'expires'
STATUS = u'status'

MAX_LENGTH_ALLOWED = u'max length allowed'
GREATER_THAN_MAX_LENGTH_ALLOWED = u'greater than max length allowed'
MAX_LENGTH_ALLOWED_AND_TEN_LEVELS = u'max length allowed and ten levels'
GREATER_THAN_MAX_LENGTH_ALLOWED_AND_TEN_LEVELS = u'greater than max length allowed and ten levels'
MAX_LENGTH_ALLOWED_AND_ELEVEN_LEVELS = u'max length allowed and eleven levels'
THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST = u'the same value of the previous request'
REPLACE_HOST = u'replace_host'
CHARS_ALLOWED = string.ascii_letters + string.digits + u'_'  # regular expression: [a-zA-Z0-9_]+
SERVICE_MAX_CHARS_ALLOWED = 50
SERVICE_PATH_LEVELS = 10
FIWARE_SERVICE = u'Fiware-Service'
FIWARE_SERVICE_PATH = u'Fiware-ServicePath'
RANDOM_ENTITIES_LABEL = [ATTRIBUTES_NAME, ATTRIBUTES_VALUE, ATTRIBUTES_TYPE, METADATAS_NAME, METADATAS_VALUE,
                         METADATAS_TYPE, ENTITIES_ID, ENTITIES_TYPE]
RANDOM_SUBSCRIPTION_LABEL = [SUBJECT_TYPE, SUBJECT_ID, SUBJECT_IDPATTERN, CONDITION_ATTRS, NOTIFICATION_ATTRS, DESCRIPTION]
RANDOM_QUERIES_PARAMETERS_LABELS = ["options"]

__logger__ = logging.getLogger("utils")


class CB:
    """
    manage Context broker operations
           - **constructor**: define protocol, host, and port used in requests. Initialize all context dict (headers, entity, parameters, subscription)

    operations:

         #### Generals:
           - **get_version_request**: return the Context Broker version installed
           - **get_statistics_request**: return the Context Broker statistics
           - **get_cache_statistics_request**: return the Context Broker cache statistics
           - **get_base_request**: offers the initial API affordances in the form of the links in the JSON body
           - **harakiri**: Orion context broker exits in an ordered manner
           - **is_cb_started**: determine whether cb is started or not
           - **definition_headers**: definition of headers using a table of data.
           - **modification_headers**: modification or append of headers and determine if the previous headers are kept or not ( true | false )

         #### Entity:
           - **properties_to_entities**: definition of properties to entities
           - **create_entities**: create N entities in modes diferents (POST /v2/entities/). the prefixes use a table of data.
           - **create_entity_raw**: create an entity with an attribute and raw values (compound, vector, boolean, integer, etc) in differents modes. It is similar to "create_entities" operation.
           - **list_all_entities**: list all entities (GET /v2/entities/). Queries parameters use a tabla of data.
           - **list_an_entity_by_id**: get an entity by ID (GET v2/entities/<entity_id>). Queries parameters use a tabla of data.
           - **list_an_attribute_by_id**: get an attribute or an attribute value by ID. Queries parameters use a tabla of data.
           - **get_entity_types**: get entity types (GET /v2/types). Queries parameters use a tabla of data.
           - **update_or_append_an_attribute_by_id**: update or append an attribute by id (POST, PATCH, PUT /v2/entities/<entity_id>). Queries parameters use a tabla of data.
           - **update_or_append_an_attribute_in_raw_by_id**: update or append an entity with raw value per special cases (compound, vector, boolean, integer, etc). It is similar to "update_or_append_an_attribute_by_id" operation.
           - **update_an_attribute_by_id_and_by_name**: update an attribute or an attribute value by ID and attribute name if it exists. Queries parameters use a tabla of data.
           - **update_an_attribute_by_id_and_by_name_in_raw_mode**: update an attribute by ID and attribute name if it exists in raw mode. It is similar to "update_an_attribute_by_id_and_by_name" operation.
           - **delete_entities_by_id**: delete entities or attribute

        ### Subscription:
           - **properties_to_subcription**: definition of properties to subscription
           - **create_subscription**: create a subscription (POST /v2/subscriptions/)
           - **create_subscription_in_raw_mode**: create a subscription in raw mode (POST /v2/subscriptions/)
           - **get_subscription_by_id**: get a subscription by id

        #### Get used values per the library:
           - **get_entity_context**: return entities contexts (dict)
           - **get_headers**: return headers (dict)
           - **get_entities_parameters**: return queries parameters (dict)
           - **get_entities_prefix**: return if entity id or entity type are used as prefix (dict)
           - **get_entity_id_to_request**: return entity id used in request to get an entity, used to verify if the entity returned is the expected (string)
           - **get_entity_type_to_request**: return entity type used in request to get/delete an entity, used to verify if the entity returned is the expected (string)
           - **get_attribute_name_to_request**: return attribute name used in request to get an attribute, used to verify if the attribute returned is the expected (string)
           - **get_subscription_context**: return queries parameters (dict)
    """

    def __init_entity_context_dict(self):
        """
        initialize entity_context dict (used in create, update or append entity)
        """
        self.entity_context = {ENTITIES_NUMBER: 1,
                               ENTITIES_TYPE: NONE,      # entity type prefix.
                               ENTITIES_ID: None,        # entity id prefix.
                               ENTITIES_PREFIX: EMPTY,   # allowed values(id | type)  -->  pending to modify in another PR, because it is used in all features
                               ATTRIBUTES_NUMBER: 0,
                               ATTRIBUTES_NAME: None,
                               ATTRIBUTES_VALUE: None,
                               ATTRIBUTES_TYPE: NONE,
                               METADATAS_NUMBER: 0,
                               METADATAS_NAME: None,
                               METADATAS_TYPE: NONE,
                               METADATAS_VALUE: None}

    def __init_subscription_context_dict(self):
        """
        initialize subscription_context dict (used in create or update subcription)
        """
        self.subscription_context = {DESCRIPTION: None,
                                     SUBJECT_TYPE: None,
                                     SUBJECT_ID: None,
                                     SUBJECT_IDPATTERN: None,
                                     SUBJECT_ENTITIES_NUMBER: 1,
                                     SUBJECT_ENTITIES_PREFIX: EMPTY, # allowed values(id | type)
                                     CONDITION_ATTRS: None,
                                     CONDITION_ATTRS_NUMBER: 0,
                                     CONDITION_EXPRESSION: None,
                                     NOTIFICATION_ATTRS: None,
                                     NOTIFICATION_ATTRS_NUMBER: 0,
                                     NOTIFICATION_ATTRSFORMAT: None,
                                     NOTIFICATION_HTTP_URL: None,
                                     NOTIFICATION_HTTP_HEADERS: None,
                                     NOTIFICATION_HTTP_QS: None,
                                     NOTIFICATION_HTTP_METHOD: None,
                                     NOTIFICATION_HTTP_PAYLOAD: None,
                                     THROTTLING: 0,
                                     EXPIRES: None,
                                     STATUS: None}

    def __init__(self, **kwargs):
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

        # initialice all dictionaries
        self.headers = {}
        self.__init_entity_context_dict()
        self.__init_subscription_context_dict()
        self.entities_parameters = {}

    # ------------------------------------Generals --------------------------------------------
    # start, stop and verifications of CB
    def get_version_request(self):
        """
        get the context broker version
        :return response to an HTTP request
        """
        header = {"Accept": "application/json"}
        resp = self.__send_request(GET, VERSION, headers=header)

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
        resp = self.__send_request(GET, "statistics", headers=header)

        assert resp.status_code == 200, " ERROR - status code in context broker statistics request. \n " \
                                        " status code: %s \n " \
                                        " body: %s" % (resp.status_code, resp.text)
        __logger__.info(" -- status code is 200 OK in statistics request")
        return resp

    def get_cache_statistics_request(self):
        """
        get context broker cache statistics
        :return: response to an HTTP request
        """
        header = {"Accept": "application/json"}
        resp = self.__send_request(GET, "cache/statistics", headers=header)

        assert resp.status_code == 200, " ERROR - status code in context broker cache statistics request. \n " \
                                        " status code: %s \n " \
                                        " body: %s" % (resp.status_code, resp.text)
        __logger__.info(" -- status code is 200 OK in cache statistics request")
        return resp

    def get_base_request(self):
        """
        get a API entry point request
        :return response to an HTTP request
        """
        header = {"Accept": "application/json"}
        resp = self.__send_request(GET, "v2", headers=header)

        assert resp.status_code == 200, " ERROR - status code in context broker base request. \n" \
                                        " status code: %s \n " \
                                        " body: %s" % (resp.status_code, resp.text)
        __logger__.info(" -- status code is 200 OK in API entry point request")
        return resp

    def harakiri(self):
        """
        Orion context broker exits in an ordered manner
        # hint: the -harakiri option is used to kill contextBroker (must be compiled in DEBUG mode)
        """
        try:
            url = "%s/%s" % (self.cb_url, "exit/harakiri")
            resp = requests.get(url=url)
            return resp.status_code
        except Exception, e:
            return -1

    def is_cb_started(self):
        """
        determine whether cb is started or not
        """
        try:
            url = "%s/%s" % (self.cb_url, "version")
            resp = requests.get(url=url)
            __logger__.debug("CB code returned with version request is: %s " % str(resp.status_code))
            return resp.status_code == 200
        except Exception, e:
            return False

    def definition_headers(self, context):
        """
        definition of headers
           | parameter          | value            |
           | Fiware-Service     | happy_path       |
           | Fiware-ServicePath | /test            |
           | Content-Type       | application/json |
           | Accept             | application/json |
        Hint: if value is "max length allowed", per example, it is random value with max length allowed and characters
              allowed
        :param context: context variable with headers
        """
        for row in context.table:
            self.headers[row[PARAMETER]] = row[VALUE]

        if FIWARE_SERVICE in self.headers:
            if self.headers[FIWARE_SERVICE] == MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE] = string_generator(SERVICE_MAX_CHARS_ALLOWED, CHARS_ALLOWED)
            elif self.headers[FIWARE_SERVICE] == GREATER_THAN_MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE] = string_generator(SERVICE_MAX_CHARS_ALLOWED + 1, CHARS_ALLOWED)

        if FIWARE_SERVICE_PATH in self.headers:
            if self.headers[FIWARE_SERVICE_PATH] == MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED)
            elif self.headers[FIWARE_SERVICE_PATH] == GREATER_THAN_MAX_LENGTH_ALLOWED:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED + 1)
            elif self.headers[FIWARE_SERVICE_PATH] == MAX_LENGTH_ALLOWED_AND_TEN_LEVELS:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED,
                                                                                 SERVICE_PATH_LEVELS)
            elif self.headers[FIWARE_SERVICE_PATH] == GREATER_THAN_MAX_LENGTH_ALLOWED_AND_TEN_LEVELS:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED + 1,
                                                                                 SERVICE_PATH_LEVELS)
            elif self.headers[FIWARE_SERVICE_PATH] == MAX_LENGTH_ALLOWED_AND_ELEVEN_LEVELS:
                self.headers[FIWARE_SERVICE_PATH] = self.__generate_service_path(SERVICE_MAX_CHARS_ALLOWED,
                                                                                 SERVICE_PATH_LEVELS + 1)
        __logger__.debug("Headers: %s" % str(self.headers))

    def modification_headers(self, context, prev):
        """
        modification or append of headers
           | parameter          | value            |
           | Fiware-Service     | happy_path       |
           | Fiware-ServicePath | /test            |
           | Content-Type       | application/json |
           | Accept             | application/json |
        :param context: context variable with headers
        :param prev:determine if the previous headers are kept or not ( true | false )
        """
        if prev.lower() != TRUE:
            self.headers.clear()
        for row in context.table:
            self.headers[row[PARAMETER]] = row[VALUE]

    def append_new_header(self, key, value):
        """
        append a new header
        :param key: header name
        :param value: header value
        """
        self.headers[key] = value

    #  -----------------  Private methods ---------------------------

    # headers
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
            temp = "%s/%s" % (temp, string_generator(length, CHARS_ALLOWED))
        return temp

   # internal funtions
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
        :param method: http method (POST, GET, PUT, DELETE, PATCH, etc)
        :param path: url path (ex: /v2/entities)
        :param payload: json body
        :param show: is used to display request and response if they are necessary
        :return http response
        """
        headers = kwargs.get("headers", None)
        payload = kwargs.get("payload", None)
        show = kwargs.get("show", True)
        parameters = kwargs.get("parameters", None)
        __logger__.info("Request and Response are shown: %s" % show)
        if show:
            p = EMPTY
            self.request_string = EMPTY
            self.response_string = EMPTY
            if parameters is not None and parameters != {}:
                for item in parameters:
                    p = '%s&%s=%s' % (p, item, parameters[item])
                p_t = list(p)
                p_t[0] = "?"
                p = "".join(p_t)
            self.request_string = "url: %s %s/%s%s" % (method, self.cb_url, path, p)

            if headers is not None:
                self.request_string = "%s\nheaders:" % self.request_string
                for item in headers:
                    self.request_string = "%s\n    %s: %s" % (self.request_string, item, headers[item])
            if payload is not None:
                self.request_string = "%s\npayload: %s" % (self.request_string, payload)
                self.request_string = "%s\npayload length: %s" % (self.request_string, str(len(payload)))
            __logger__.debug("----------------- Request ---------------------------------\n%s" % self.request_string)
            __logger__.debug("-----------------------------------------------------------")
        url = "%s/%s" % (self.cb_url, path)
        try:
            resp = requests.request(method=method, url=url, headers=headers, data=payload, params=parameters)
        except Exception, e:
            assert False, "ERROR  - send request \n     - url: %s\n    - %s" % (url, str(e))
        if show:
            self.response_string = "http code: %s - %s" % (resp.status_code, resp.reason)
            self.response_string = "%s\nheaders:" % self.response_string
            for h in resp.headers:
                self.response_string = "%s\n   %s: %s" % (self.response_string, h, resp.headers[h])
            self.response_string = "%s\npayload: %s " % (self.response_string, resp.text)
            __logger__.debug("----------------- Response ---------------------------------\n%s" % self.response_string)
            __logger__.debug("------------------------------------------------------------")
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
            quote_exist = False
            if random_label in random_labels:
                if (dictionary[random_label] is not None) and (dictionary[random_label].find(RANDOM) >= 0):
                    if dictionary[random_label].find("\"") >= 0:
                        quote_exist = True
                    dictionary[random_label] = string_generator(self.__get_random_number(remove_quote(dictionary[random_label])))
                    if quote_exist:
                        dictionary[random_label] = '"%s"' % dictionary[random_label]
        return dictionary

    # create entity/ies dinamically or manually
    def __create_metadata(self, metadata_number, metadata_name, metadata_type, metadata_value):
        """
        create N metadatas dynamically. The value could be random value ("random").
        :param metadata_number: number of metadatas
        :param metadata_name: name of metadatas with a prefix plus a consecutive
        :param metadata_value: metadatas value.
        :param metadata_typee: metadatas type.
        :return metadatas dict
        """
        meta_dict = {}
        if metadata_name is not None:
            for i in range(int(metadata_number)):
                if int(metadata_number) > 1:
                    name = "%s_%s" % (metadata_name, str(i))
                else:
                    name = metadata_name
                meta_dict[name] = {}
                if metadata_value is not None:
                    meta_dict[name][VALUE] = metadata_value
                if metadata_type != NONE:
                    meta_dict[name][TYPE] = metadata_type
        return meta_dict

    def __create_attributes(self, entity_context, mode):
        """
        create attributes with entity context
        :return (dict) attribute list
        """
        attr = {}
        attributes = {}
        metadata = {}

        # create metadatas if they exist
        if int(entity_context[METADATAS_NUMBER]) > 0:
            metadata = self.__create_metadata(entity_context[METADATAS_NUMBER], entity_context[METADATAS_NAME],
                                              entity_context[METADATAS_TYPE], entity_context[METADATAS_VALUE])
        __logger__.debug("Metadatas: %s" % str(metadata))

        # create attributes
        if mode == NORMALIZED:
            if metadata != {}:
                attr[METADATA] = metadata
            if entity_context[ATTRIBUTES_TYPE] != NONE:
                attr[TYPE] = entity_context[ATTRIBUTES_TYPE]
            if entity_context[ATTRIBUTES_VALUE] is not None:
                attr[VALUE] = entity_context[ATTRIBUTES_VALUE]
        elif mode == KEY_VALUES:
            if entity_context[ATTRIBUTES_VALUE] is not None:
                attr = entity_context[ATTRIBUTES_VALUE]

        if entity_context[ATTRIBUTES_NAME] is not None:
            for i in range(int(entity_context[ATTRIBUTES_NUMBER])):
                if int(entity_context[ATTRIBUTES_NUMBER]) > 1:
                    name = "%s_%s" % (entity_context[ATTRIBUTES_NAME], str(i))
                else:
                    name = entity_context[ATTRIBUTES_NAME]
                attributes[name] = attr
        return attributes

    def __create_attribute_raw(self, entity_context, mode):
        """
        create an attribute with entity context in raw mode
        :return (string)
        """
        attribute_str = EMPTY
        # create attribute with/without attribute type and metadatas (with/without type)
        if mode == NORMALIZED:
            # append attribute type if it does exist
            if entity_context[ATTRIBUTES_TYPE] != NONE:
                attribute_str = '"type": %s' % self.entity_context[ATTRIBUTES_TYPE]

            # append metadata if it does exist
            if entity_context[METADATAS_NAME] is not None:
                if entity_context[METADATAS_TYPE] != NONE:
                    metadata = '"metadata": {%s: {"value": %s, "type": %s}}' % (entity_context[METADATAS_NAME],
                                                                                entity_context[METADATAS_VALUE],
                                                                                entity_context[METADATAS_TYPE])
                else:
                    metadata = '"metadata": {%s: {"value": %s}}' % (entity_context[METADATAS_NAME],
                                                                    entity_context[METADATAS_VALUE])
                if attribute_str != EMPTY:
                    attribute_str = '%s, %s' % (attribute_str, metadata)
                else:
                    attribute_str = metadata

            # append attribute value if it exist
            if entity_context[ATTRIBUTES_VALUE] is not None:
                if attribute_str != EMPTY:
                    attribute_str = '%s, "value": %s' % (attribute_str, entity_context[ATTRIBUTES_VALUE])
                else:
                    attribute_str = '"value": %s' % entity_context[ATTRIBUTES_VALUE]

            # append attribute name
            if entity_context[ATTRIBUTES_NAME] is not None:
                attribute_str = u'%s:{%s}' % (entity_context[ATTRIBUTES_NAME], attribute_str)

        elif mode == KEY_VALUES and entity_context[ATTRIBUTES_NAME] is not None:
            attribute_str = u'%s:{%s}' % (entity_context[ATTRIBUTES_NAME], attribute_str)
            attribute_str = u'%s: %s' % (entity_context[ATTRIBUTES_NAME], entity_context[ATTRIBUTES_VALUE])

        __logger__.debug("Atribute with raw values: %s" % attribute_str)
        return attribute_str

    def __create_attributes_values(self, entity_context):
        """
        create attribute values to update by id and name
        :param entity_context: new context to update
        :return dict
        """
        attribute = {}
        # append attribute type, attribute metadatas and attribute value if the first two exist for one attribute
        if entity_context[METADATAS_NUMBER] is not None:
            metadata = self.__create_metadata(entity_context[METADATAS_NUMBER], entity_context[METADATAS_NAME],
                                               entity_context[METADATAS_TYPE], entity_context[METADATAS_VALUE])
            if metadata != {}: attribute[METADATA] = metadata
        __logger__.debug("Metadatas: %s" % str(attribute))
        if entity_context[ATTRIBUTES_TYPE] != NONE:
            attribute["type"] = entity_context[ATTRIBUTES_TYPE]
        if entity_context[ATTRIBUTES_VALUE] is not None:
            attribute["value"] = entity_context[ATTRIBUTES_VALUE]
        __logger__.debug("Attribute: %s" % str(attribute))
        return attribute

    def __create_attribute_by_id_attr_name_raw(self, entity_context):
        """
        create attribute context (value, type and/or metadata) to update attributes by id and attribute name
        with entity context in raw mode
        :return (string)
        """
        attribute_str = "{"
        attr_context = []  # attr_context constains attribute value, attribute type and attribute metadatas

        # create attribute context with/without attribute value, attribute type and metadatas (with/without type)
        if entity_context[ATTRIBUTES_VALUE] is not None:
            attr_context.append('"value": %s' % self.entity_context[ATTRIBUTES_VALUE])

        if entity_context[ATTRIBUTES_TYPE] != NONE:
            attr_context.append('"type": %s' % self.entity_context[ATTRIBUTES_TYPE])

        if entity_context[METADATAS_NAME] is not None:
            if entity_context[METADATAS_TYPE] != NONE:
                attr_context.append('"metadata": {%s: {"type": %s, "value": %s}}' % (entity_context[METADATAS_NAME],
                                                                                     entity_context[METADATAS_TYPE],
                                                                                     entity_context[METADATAS_VALUE]))
            else:
                attr_context.append('"metadata": {%s: {"value": %s}}' % (entity_context[METADATAS_NAME], entity_context[METADATAS_VALUE]))

        for item in attr_context:
            attribute_str = "%s %s," % (attribute_str, item)

        attribute_str = "%s }" % attribute_str[:-1]
        __logger__.debug("Atribute: %s" % attribute_str)
        return attribute_str

    def __create_subsc_entities(self, subscription_context):
        """
        create N entities to subscription request
        :param subscription_context: subscription_context dict
        :return list
        """
        entities= []
        for e in range(int(subscription_context[SUBJECT_ENTITIES_NUMBER])):
            entity = {}
            if subscription_context[SUBJECT_IDPATTERN] is not None:
                entity[IDPATTERN] = subscription_context[SUBJECT_IDPATTERN]
            if subscription_context[SUBJECT_ID] is not None:
                if subscription_context[SUBJECT_ENTITIES_PREFIX] == ID and subscription_context[SUBJECT_ENTITIES_NUMBER] > 1:
                    entity[ID] = "%s_%s" % (subscription_context[SUBJECT_ID], str(e))
                else:
                    entity[ID] = subscription_context[SUBJECT_ID]
            if subscription_context[SUBJECT_TYPE] is not None:
                if subscription_context[SUBJECT_ENTITIES_PREFIX] == TYPE and subscription_context[SUBJECT_ENTITIES_NUMBER] > 1:
                    entity[TYPE] = "%s_%s" % (subscription_context[SUBJECT_TYPE], str(e))
                else:
                    entity[TYPE] = subscription_context[SUBJECT_TYPE]
            entities.append(entity)
        return entities

    def __create_subsc_condition(self, subscription_context):
        """
        append attributes and expression conditions
        :param subscription_context: subscription_context dict
        :return dict
        """
        ATTRS_FIELD_NAME = u'attrs'
        EXPRESSION_FIELD_NAME = u'expression'
        condition = {}
        # attributes field
        if subscription_context[CONDITION_ATTRS] == u'array is empty':
            condition[ATTRS_FIELD_NAME] = []
        elif subscription_context[CONDITION_ATTRS] is not None:
            attrs = []
            for a in range(int(subscription_context[CONDITION_ATTRS_NUMBER])):
                if int(subscription_context[CONDITION_ATTRS_NUMBER]) > 1:
                    attrs.append("%s_%s" % (subscription_context[CONDITION_ATTRS], str(a)))
                else:
                    attrs.append(subscription_context[CONDITION_ATTRS])
            condition[ATTRS_FIELD_NAME] = attrs
        # expression field
        if subscription_context[CONDITION_EXPRESSION] == u'object is empty':
            condition[EXPRESSION_FIELD_NAME] = {}
        elif subscription_context[CONDITION_EXPRESSION] is not None:
            condition[EXPRESSION_FIELD_NAME] = {}
            exp_op = subscription_context[CONDITION_EXPRESSION].split("&")
            for op in exp_op:
                exp_split = op.split(">>>")
                condition[EXPRESSION_FIELD_NAME][exp_split[0]] = exp_split[1]
        return condition

    def __create_subsc_notification(self, subscription_context):
        """
        append notification fields (callback, attributes, throttling, headers, formarAttrs, query)
        :param subscription_context: subscription_context dict
        :return dict
        """
        ATTRS_FIELD_NAME = u'attrs'
        HTTP_FIELD_NAME = u'http'
        notification = {}
        # http -url field
        http_field_exist = False
        if subscription_context[NOTIFICATION_HTTP_URL] != u'without notification http field':
            if subscription_context[NOTIFICATION_HTTP_URL] is not None:
                http_field_exist = True  # used to determine whether http dict is created or not
                notification[HTTP_FIELD_NAME] = {}
                notification[HTTP_FIELD_NAME]["url"] = subscription_context[NOTIFICATION_HTTP_URL]

            # peding to develop (headers, qs, method and payload)
            if subscription_context[NOTIFICATION_HTTP_HEADERS] is not None:
                if not http_field_exist:
                    http_field_exist = True  # used to determine whether http dict is created or not
                    notification[HTTP_FIELD_NAME] = {}
                notification[HTTP_FIELD_NAME]["headers"] = subscription_context[NOTIFICATION_HTTP_HEADERS]
            if subscription_context[NOTIFICATION_HTTP_QS] is not None:
                if not http_field_exist:
                    http_field_exist = True  # used to determine whether http dict is created or not
                    notification[HTTP_FIELD_NAME] = {}
                notification[HTTP_FIELD_NAME]["query"] = subscription_context[NOTIFICATION_HTTP_QS]
            if subscription_context[NOTIFICATION_HTTP_METHOD] is not None:
                if not http_field_exist:
                    http_field_exist = True  # used to determine whether http dict is created or not
                    notification[HTTP_FIELD_NAME] = {}
                notification[HTTP_FIELD_NAME]["method"] = subscription_context[NOTIFICATION_HTTP_METHOD]
            if subscription_context[NOTIFICATION_HTTP_PAYLOAD] is not None:
                if not http_field_exist:
                    http_field_exist = True  # used to determine whether http dict is created or not
                    notification[HTTP_FIELD_NAME] = {}
                notification[HTTP_FIELD_NAME]["payload"] = subscription_context[NOTIFICATION_HTTP_PAYLOAD]

        # attrs field
        if subscription_context[NOTIFICATION_ATTRS] == u'array is empty':
            notification[ATTRS_FIELD_NAME] = []
        elif subscription_context[NOTIFICATION_ATTRS] is not None:
            attrs = []
            for a in range(int(subscription_context[NOTIFICATION_ATTRS_NUMBER])):
                if int(subscription_context[NOTIFICATION_ATTRS_NUMBER]) > 1:
                    attrs.append("%s_%s" % (subscription_context[NOTIFICATION_ATTRS], str(a)))
                else:
                   attrs.append(subscription_context[NOTIFICATION_ATTRS])
            notification[ATTRS_FIELD_NAME] = attrs

        # attrsFormat field (pending to develop)
        if subscription_context[NOTIFICATION_ATTRSFORMAT] is not None:
            notification["attrsFormat"] = subscription_context[NOTIFICATION_ATTRSFORMAT]
        return notification

    def __create_subsc_subject_raw(self, subscription_context):
        """
        create subject field (entities and condition) to subscriptions in raw mode
        :return string
        """
        # entities fields
        entities = u'"entities": [{'
        # type field
        if subscription_context[SUBJECT_TYPE] is not None:
            entities = u'%s"type": %s,' % (entities, subscription_context[SUBJECT_TYPE])
        # id field
        if subscription_context[SUBJECT_ID] is not None:
            entities = u'%s"id": %s}],' % (entities, subscription_context[SUBJECT_ID])
        # idPattern field
        if subscription_context[SUBJECT_IDPATTERN] is not None:
            entities = u'%s"idPattern": %s}],' % (entities, subscription_context[SUBJECT_IDPATTERN])
        # condition fields
        condition = u'"condition": {'
        # attributes field
        if subscription_context[CONDITION_ATTRS] is not None:
            condition = u'%s "attrs": [%s]' % (condition, subscription_context[CONDITION_ATTRS])
            if subscription_context[CONDITION_EXPRESSION] is not None:
                condition = "%s," % condition
        # expression field
        if subscription_context[CONDITION_EXPRESSION] is not None:
            exp_op = subscription_context[CONDITION_EXPRESSION].split("&")
            internal_conditions = EMPTY
            for op in exp_op:
                exp_split = op.split(">>>")
                internal_conditions = u' %s %s: %s,' % (internal_conditions, exp_split[0], exp_split[1])
            condition = u'%s "expression": {%s}' % (condition, internal_conditions[:-1])
        condition = u'%s }' % condition
        return  u'"subject": {%s %s}' % (entities, condition)

    def __create_subsc_notification_raw(self, subscription_context):
        """
        create notification fields (callback, attributes, throttling, headers, query and attrsFormat) to subscription in raw mode
        :return string
        """
        url = EMPTY
        attributes = EMPTY
        throttling = EMPTY
        headers = EMPTY
        query = EMPTY
        attrsFormat = EMPTY
        notification = EMPTY
        http_field_exist = False
        # http url field
        if subscription_context[NOTIFICATION_HTTP_URL] is not None:
            if not http_field_exist:
                http_field_exist = True  # used to determine whether http dict is created or not
                notification = u'"http": {'
            notification = u'%s "url": %s,' % (notification, subscription_context[NOTIFICATION_HTTP_URL])
        # pending to develop
        if subscription_context[NOTIFICATION_HTTP_HEADERS] is not None:
            if not http_field_exist:
                http_field_exist = True  # used to determine whether http dict is created or not
                notification = u'"http": {'
            notification = u'%s "headers": %s,' % (notification, subscription_context[NOTIFICATION_HTTP_HEADERS])
        if subscription_context[NOTIFICATION_HTTP_QS] is not None:
            if not http_field_exist:
                http_field_exist = True  # used to determine whether http dict is created or not
                notification = u'"http": {'
            notification = u'%s "qs": %s,' % (notification, subscription_context[NOTIFICATION_HTTP_QS])
        if subscription_context[NOTIFICATION_HTTP_METHOD] is not None:
            if not http_field_exist:
                http_field_exist = True  # used to determine whether http dict is created or not
                notification = u'"http": {'
            notification = u'%s "method": %s,' % (notification, subscription_context[NOTIFICATION_HTTP_METHOD])
        if subscription_context[NOTIFICATION_HTTP_PAYLOAD] is not None:
            if not http_field_exist:
                http_field_exist = True  # used to determine whether http dict is created or not
                notification = u'"http": {'
            notification = u'%s "payload": %s,' % (notification, subscription_context[NOTIFICATION_HTTP_PAYLOAD])
        if notification != EMPTY:
            notification = u'%s},' % notification[:-1]

        # attrsFormat field
        if subscription_context[NOTIFICATION_ATTRSFORMAT] is not None:
            attrsFormat = u'"attrsFormat": %s,' % subscription_context[NOTIFICATION_ATTRSFORMAT]
            notification = "%s %s" % (notification, attrsFormat)

        # attributes field
        if subscription_context[NOTIFICATION_ATTRS] is not None:
            attributes = u'"attrs": [%s],' % (subscription_context[NOTIFICATION_ATTRS])
            notification = "%s %s" % (notification, attributes)

        if notification != EMPTY:
            notification = u'{%s}' % notification[:-1]

        return u'"notification": %s' % notification

    # -------------------- Entities -------------------------------------------------

    # properties to entities
    def properties_to_entities(self, context):
        """
        definition of properties to entities
          | parameter         | value                   |
          | entities_type     | room                    |
          | entities_id       | room2                   |
          | attributes_number | 2                       |
          | attributes_name   | random=5                |
          | attributes_value  | 017-06-17T07:21:24.238Z |
          | attributes_type   | date                    |
          | metadatas_number  | 2                       |
          | metadatas_name    | very_hot                |
          | metadatas_type    | alarm                   |
          | metadatas_value   | hot                     |
          #  query parameter
          | qp_options        | keyvalue                |
        Hint: - If attributes number is equal "1", the attribute name has not suffix, ex: `attributes_name=temperature`
                else attributes number is major than "1" the attributes name are value plus a suffix (consecutive), ex:
                  `attributes_name=temperature_0, attributes_name=temperature_1, ..., temperature_N`
              - If would like a query parameter name, use `qp_` prefix into `properties to entities` step
              - It is possible to use the same value of the previous request in another request using this string:
                  `the same value of the previous request`.
              - "attr_name", "attr_value", "attr_type", "meta_name", "meta_type" and "meta_value" could be random values.
                 The number after "=" is the number of chars
                     ex: | attributes_name | random=10 |
              - if we wanted an empty payload in a second request, use:
                      | parameter          |
                      | without_properties |
        :param context: context variable with properties to entities
        """
        # store previous entities context dict temporally (used in update request)
        self.dict_temp = {}
        for item in self.entity_context:
            self.dict_temp[item] = self.entity_context[item]

        # store parameters in entities contexts
        self.__init_entity_context_dict()  # reinit context dict (used in update request)
        if context.table is not None:
            for row in context.table:
                if row[PARAMETER] in self.entity_context:
                    self.entity_context[row[PARAMETER]] = row[VALUE]
                elif row[PARAMETER] == u'without_properties':
                    break
                elif row[PARAMETER].find("qp_") >= 0:
                    qp = str(row[PARAMETER]).split("qp_")[1]
                    self.entities_parameters[qp] = row[VALUE]
                else:
                    __logger__.warn("Wrong parameter: %s" % row[PARAMETER])

        # The same value from create request (used in update request)
        for item in self.entity_context:
            if self.entity_context[item] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.entity_context[item] = self.dict_temp[item]

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)
        self.entities_parameters = self.__random_values(RANDOM_QUERIES_PARAMETERS_LABELS, self.entities_parameters)

        if self.entity_context[ATTRIBUTES_NAME] is not None and self.entity_context[ATTRIBUTES_NUMBER] == 0:
            self.entity_context[ATTRIBUTES_NUMBER] = 1
        if self.entity_context[METADATAS_NAME] is not None and self.entity_context[METADATAS_NUMBER] == 0:
            self.entity_context[METADATAS_NUMBER] = 1

        # log entities contexts
        __logger__.debug("entity context properties:")
        for item in self.entity_context:
            __logger__.debug("   - %s: %s" % (item, self.entity_context[item]))

        # log entities_parameters
        __logger__.debug("queries parameters:")
        for item in self.entities_parameters:
            __logger__.debug("   - %s: %s" % (item, self.entities_parameters[item]))

    # create entity/entities
    def create_entities(self, context, entities_number, mode):
        """
        create N entities in modes diferents
        :request -> POST /v2/entities/
        :payload --> Yes
        :query parameters --> Yes
        :param context: context variable (prefixes)
        :param entities_number: number of entities
        :param mode: mode in that will be created the entity (normalized | keyValues | values),
                     it is not the query parameter (options), else the mode to generate the request.
                     normalized:
                                "attr": {
                                     "value": "45",
                                     ...
                                }
                     keyValues:
                                "attr": "45"
        Hints:
            - If entity id prefix is true, the entity id is value plus a suffix (consecutive), ex:
                 `entity_id=room_0, entity_id=room_1, ..., entity_id=room_N`
            - If entity type prefix is true, the entity type is value plus a suffix (consecutive), ex:
                 `entity_type=room_0, entity_type=room_1, ..., entity_type=room_N`
            - The prefixes function (id or type) are used if entities_number is greater than 1.

        :return responses list
        """
        resp_list = []
        self.prefixes = {ID: False,
                         TYPE: False}
        # prefixes
        if context.table is not None:
            for row in context.table:
                if row[ENTITY] in self.prefixes:
                    self.prefixes[row[ENTITY]] = row[PREFIX]
        self.entity_context[ENTITIES_NUMBER] = int(entities_number)

        # log id and type prefixes
        __logger__.debug("id prefix  : %s" % self.prefixes[ID])
        __logger__.debug("type prefix: %s" % self.prefixes[TYPE])

        # create attributes with entity context
        entity = self.__create_attributes(self.entity_context, mode)
        __logger__.debug("attributes: %s" % str(entity))

        # if options=keyValues the attribute values is all. Attribute_type and metadata(s) are restarted
        if OPTIONS in self.entities_parameters and self.entities_parameters[OPTIONS] == KEY_VALUES:
            if self.entity_context[ATTRIBUTES_NUMBER] == 0:
                self.entity_context[ATTRIBUTES_VALUE] = entity[self.entity_context[ATTRIBUTES_NAME]]
            else:
                self.entity_context[ATTRIBUTES_VALUE] = entity["%s_0" % self.entity_context[ATTRIBUTES_NAME]]
            self.entity_context[ATTRIBUTES_TYPE] = NONE
            self.entity_context[METADATAS_NUMBER] = 0
            self.entity_context[METADATAS_NAME] = None

        # create N consecutive entities with prefixes or not
        for e in range(self.entity_context[ENTITIES_NUMBER]):
            if self.entity_context[ENTITIES_ID] is not None:
                if self.prefixes[ID] and self.entity_context[ENTITIES_NUMBER] > 1:
                    entity_id = "%s_%s" % (self.entity_context[ENTITIES_ID], str(e))
                else:
                    entity_id = self.entity_context[ENTITIES_ID]
                entity[ID] = entity_id
            if self.entity_context[ENTITIES_TYPE] != NONE:
                if self.prefixes[TYPE] and self.entity_context[ENTITIES_NUMBER] > 1:
                    entity_type = "%s_%s" % (self.entity_context[ENTITIES_TYPE], str(e))
                else:
                    entity_type = self.entity_context[ENTITIES_TYPE]
                entity[TYPE] = entity_type

            # request
            payload = convert_dict_to_str(entity, JSON)
            if entity != {}:
                resp_list.append(self.__send_request(POST, V2_ENTITIES, headers=self.headers,
                                                     parameters=self.entities_parameters, payload=payload))
            else:
                resp_list.append(self.__send_request(POST, V2_ENTITIES, parameters=self.entities_parameters,
                                                     headers=self.headers))
        return resp_list

    def create_entity_raw(self, context, mode):
        """
        create an entity with an attribute and raw values (compound, vector, boolean, integer, etc) in differents modes
        :request -> POST /v2/entities/
        :payload --> Yes
        :query parameters --> Yes
        :param mode: mode in that will be created the entity (normalized | keyValues | values),
                     it is not the query parameter (options), else the mode to generate the request.
                     normalized:
                                "attr": {
                                     "value": "45",
                                     ...
                                }
                     keyValues:
                                "attr": "45"
        Some cases are not parsed correctly to dict in python.
           ex of raw values:
             "value": true
             "value": false
             "value": 34
             "value": 5.00002
             "value": [ "json", "vector", "of", 6, "strings", "and", 2, "integers" ]
             "value": {"x": {"x1": "a","x2": "b"}}
             "value": "41.3763726, 2.1864475,14"  -->  "type": "geo:point"
             "value": "2017-06-17T07:21:24.238Z"  -->  "type: "date"
        :return responses list
        """
        entity = EMPTY
        attribute_str = EMPTY
        self.entity_context[ENTITIES_NUMBER] = 1
        self.entity_context[ATTRIBUTES_NUMBER] = 1

        # create attribute with/without attribute type and metadatas (with/without type)
        attribute_str = self.__create_attribute_raw(self.entity_context, mode)

        # if options=keyValues the attribute values is all. Attribute_type and metadata(s) are restarted
        if OPTIONS in self.entities_parameters and self.entities_parameters[OPTIONS] == KEY_VALUES:
            key_value_attr = attribute_str.split(":")[1]
            self.entity_context[ATTRIBUTES_VALUE] = key_value_attr
            self.entity_context[ATTRIBUTES_TYPE] = NONE
            self.entity_context[METADATAS_NUMBER] = 0
            self.entity_context[METADATAS_NAME] = None

        # create entity with attribute value in raw
        if self.entity_context[ENTITIES_TYPE] != NONE:
            entity = '"type": %s' % self.entity_context[ENTITIES_TYPE]
        if self.entity_context[ENTITIES_ID] is not None:
            if entity != EMPTY:
                entity = '%s, "id": %s' % (entity, self.entity_context[ENTITIES_ID])
            else:
                entity = '"id": %s' % self.entity_context[ENTITIES_ID]
        if attribute_str != EMPTY:
            payload = u'{%s, %s}' % (entity, attribute_str)
        else:
            payload = u'{%s}' % entity

        resp = self.__send_request(POST, V2_ENTITIES, headers=self.headers, payload=payload,
                                   parameters=self.entities_parameters)
        return resp

    # list entity/ies
    def list_all_entities(self, context):
        """
        list all entities
        :request -> GET /v2/entities/
        :payload --> No
        :query parameters --> Yes
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
        dict_temp = {}
        for item in self.entity_context:
            dict_temp[item] = self.entity_context[item]
        self.entities_parameters = {}
        __logger__.info("List all entities, filtered by the queries parameters")
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        # The same value from create request
        for item in self.entities_parameters:
            if self.entities_parameters[item] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                if item == "id":
                    self.entities_parameters[item] = remove_quote(dict_temp[ENTITIES_ID])
                elif item == "type":
                    self.entities_parameters[item] = remove_quote(dict_temp[ENTITIES_TYPE])

        # Random values in queries parameters
        dict_temp = self.__random_values(RANDOM_ENTITIES_LABEL, dict_temp)
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)
        self.entities_parameters = self.__random_values(RANDOM_QUERIES_PARAMETERS_LABELS, self.entities_parameters)

        # log queries parameters
        for item in self.entities_parameters:
            __logger__.debug("Queries parameters: %s=%s" % (item, self.entities_parameters[item]))

        resp = self.__send_request(GET, V2_ENTITIES, headers=self.headers, parameters=self.entities_parameters)
        return resp

    def list_an_entity_by_id(self, context, entity_id, attrs=EMPTY):
        """
        get an entity by ID or get attributes in an entity by ID
          | parameter | value       |
          | attrs     | temperature |
        :requests -> GET v2/entities/<entity_id>
                     GET v2/entities/<entity_id>/attrs
        :payload --> No
        :query parameters --> Yes
        Hint: if we need " char, use \' and it will be replaced (mappping_quotes)
        :return: http response
        """
        self.entity_id_to_request = mapping_quotes(entity_id)  # used to verify if the entity returned is the expected
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        # log queries parameters
        __logger__.debug("entity_id: %s" % self.entity_id_to_request)
        for item in self.entities_parameters:
            __logger__.debug("Queries parameters: %s=%s" % (item, self.entities_parameters[item]))

        resp = self.__send_request(GET, "%s/%s%s" % (V2_ENTITIES, self.entity_id_to_request, attrs), headers=self.headers,
                                   parameters=self.entities_parameters)
        return resp

    def list_an_attribute_by_id(self, context, attribute_name, entity_id, value=EMPTY):
        """
        get an attribute or an attribute value by ID
        :request --> GET v2/entities/<entity_id>/attrs/<attribute_name>/
                 --> GET v2/entities/<entity_id>/attrs/<attribute_name>/value
        :payload --> No
        :query parameters --> No
        :param entity_id: entity id used to get
        :param attribute_name: attribute to get
        :value: if you would like get full attribute use default value, but if get attribute value, the value is "value"
        :return http response
        """
        self.entities_parameters.clear()  # restart dictionary
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        dict_temp = {}
        for item in self.entity_context:
            dict_temp[item] = self.entity_context[item]
        self.__init_entity_context_dict()
        self.entity_context[ENTITIES_ID] = entity_id
        self.entity_context[ATTRIBUTES_NAME] = attribute_name

        # The same value from create request
        for item in self.entity_context:
            if self.entity_context[item] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.entity_context[item] = dict_temp[item]

        # Random values
        dict_temp = self.__random_values(RANDOM_ENTITIES_LABEL, dict_temp)
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)
        self.entities_parameters = self.__random_values(RANDOM_QUERIES_PARAMETERS_LABELS, self.entities_parameters)

        self.entity_id_to_request = mapping_quotes(
            self.entity_context[ENTITIES_ID])  # used to verify if the entity returned is the expected
        self.attribute_name_to_request = mapping_quotes(
            self.entity_context[ATTRIBUTES_NAME])  # used to verify if the attribute returned is the expected

        # log messages
        __logger__.debug("entity_id: %s" % self.entity_id_to_request)
        __logger__.debug("attribute_name: %s" % self.attribute_name_to_request)

        resp = self.__send_request(GET, "%s/%s/attrs/%s/%s" % (
            V2_ENTITIES, self.entity_id_to_request, self.attribute_name_to_request, value),
                                   headers=self.headers, parameters=self.entities_parameters)

        # update with last values
        dict_temp[ENTITIES_ID] = self.entity_context[ENTITIES_ID]
        dict_temp[ATTRIBUTES_NAME] = self.entity_context[ATTRIBUTES_NAME]
        self.entity_context = dict_temp
        return resp

    def get_entity_types(self, context):
        """
        get entity types
        :request -> GET /v2/types
        :payload --> No
        :query parameters --> Yes
            parameters:
                limit: Limit the number of types to be retrieved
                offset: Skip a number of records
                options: Possible values: count, values .
        """
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        # log queries parameters
        for item in self.entities_parameters:
            __logger__.debug("Queries parameters: %s=%s" % (item, self.entities_parameters[item]))

        resp = self.__send_request(GET, V2_TYPES, headers=self.headers, parameters=self.entities_parameters)
        return resp

    def get_an_entity_type(self, context, entity_type):
        """
        get an entity type
        :request -> GET /v2/types/<entity_type>
        :payload --> No
        :query parameters --> No
        """
        # The same value from create request
        if entity_type == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
            self.entity_type_to_request = self.entity_context[ENTITIES_TYPE]
        else:
            self.entity_type_to_request = entity_type

        # entity type in log
        __logger__.debug("Type: %s" % self.entity_type_to_request)

        resp = self.__send_request(GET , "%s/%s" % (V2_TYPES, self.entity_type_to_request), headers=self.headers)
        return resp

    # update entity
    def update_or_append_an_attribute_by_id(self, method, context, entity_id, mode):
        """
        update or append an attribute by id
        :request -> /v2/entities/<entity_id>
        :payload --> Yes
        :query parameters --> Yes
        :param method: method used in request (POST, PATCH, PUT)
        :param context: new values to update or append
        :param entity_id: entity used to update or append
        :param mode: mode in that will be created attributes in request ( normalized | keyValues | values)
        Hint: if would like a query parameter name, use `qp_` prefix
        :return http response
        """
        self.entity_context[ENTITIES_ID] = entity_id
        # The same value from create request
        for item in self.entity_context:
            if self.entity_context[ENTITIES_ID] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.entity_context[ENTITIES_ID] = self.dict_temp[ENTITIES_ID]
        self.entity_id_to_request = mapping_quotes(
            self.entity_context[ENTITIES_ID])  # used to verify if the entity returned is the expected

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)

        # create attributes with entity context
        entities = self.__create_attributes(self.entity_context, mode)

        payload = convert_dict_to_str(entities, JSON)
        if entities != {}:
            resp = self.__send_request(method, "%s/%s/attrs" % (V2_ENTITIES, self.entity_context[ENTITIES_ID]),
                                       headers=self.headers, payload=payload, parameters=self.entities_parameters)
        else:
            resp = self.__send_request(method, "%s/%s/attrs" % (V2_ENTITIES, self.entity_context[ENTITIES_ID]),
                                       headers=self.headers, parameters=self.entities_parameters)
        # update self.entity_context with last values (ex: create request)
        for item in self.entity_context:
            if (self.entity_context[item] is None) or (self.entity_context[item] == "none"):
                if item not in (ATTRIBUTES_TYPE, METADATAS_TYPE, ATTRIBUTES_VALUE):
                    self.entity_context[item] = self.dict_temp[item]

        # if options=keyValues is used, the type and metadatas are not used
        if OPTIONS in self.entities_parameters and self.entities_parameters[OPTIONS] == KEY_VALUES:
            self.entity_context[ATTRIBUTES_TYPE] = NONE
            self.entity_context[METADATAS_NUMBER] = 0
        return resp

    def update_or_append_an_attribute_in_raw_by_id(self, method, context, entity_id, mode):
        """
        update or append an entity with raw value per special cases (compound, vector, boolean, integer, etc)
        :request -> /v2/entities/<entity_id>
        :payload --> Yes
        :query parameters --> Yes
        :param method: url methods allowed (PUT | PATCH | POST)
        :param context: new context to update
        :param entity_id: entity id used to update or append
        :param mode: mode in that will be created attributes in request ( normalized | keyValues)
        Hint: if would like a query parameter name, use `qp_` prefix
            values examples:
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
        self.entity_context[ENTITIES_ID] = entity_id
        # The same value from create request
        for item in self.entity_context:
            if self.entity_context[ENTITIES_ID] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.entity_context[ENTITIES_ID] = self.dict_temp[ENTITIES_ID]
        self.entity_id_to_request = mapping_quotes(
            self.entity_context[ENTITIES_ID])  # used to verify if the entity returned is the expected

        # create attribute with/without attribute type and metadatas (with/without type)
        attribute_str = "{%s}" % self.__create_attribute_raw(self.entity_context, mode)

        resp = self.__send_request(method, "%s/%s/attrs" % (V2_ENTITIES, self.entity_context[ENTITIES_ID]),
                                   headers=self.headers, payload=attribute_str, parameters=self.entities_parameters)

        # update self.entity_context with last values (ex: create request)
        for item in self.entity_context:
            if (self.entity_context[item] is None) and (self.dict_temp[item] is not None):
                self.entity_context[item] = self.dict_temp[item]
        return resp

    def update_an_attribute_by_id_and_by_name(self, context, entity_id, attribute_name, value=EMPTY):
        """
        update an attribute or an attribute value by ID and attribute name if it exists
        :requests ->
                     value = False:  PUT  /v2/entities/<entity_id>/attrs/<attr_name>
                     value = True:   PUT  /v2/entities/<entity_id>/attrs/<attr_name>/value
        :payload --> Yes
        :query parameters --> Yes
        :param context: new context to update
        :param entity_id: entity id used to update
        :param attribute_name: attribute to update
        Hint: if would like a query parameter name, use `qp_` prefix
        :param value: is used to modify only attribute value
        :return http response
        """
        payload = EMPTY
        self.entity_context[ENTITIES_ID] = entity_id
        self.entity_context[ATTRIBUTES_NAME] = attribute_name
        # The same value from create request
        for item in self.entity_context:
            if self.entity_context[item] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.entity_context[item] = self.dict_temp[item]
        self.entity_id_to_request = mapping_quotes(
            self.entity_context[ENTITIES_ID])  # used to verify if the entity returned is the expected

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)

        # create attributes with entity context
        if value == EMPTY:
            attribute = {}
            attribute = self.__create_attributes_values(self.entity_context)
            payload = convert_dict_to_str(attribute, JSON)
            if payload == "{}": payload = EMPTY
        else:
            if self.entity_context[ATTRIBUTES_VALUE]is not None:
                payload = '"%s"' % self.entity_context[ATTRIBUTES_VALUE]

        if payload != EMPTY:
            resp = self.__send_request(PUT, "%s/%s/attrs/%s/%s" %
                        (V2_ENTITIES, self.entity_context[ENTITIES_ID], self.entity_context[ATTRIBUTES_NAME], value),
                        headers=self.headers, payload=payload, parameters=self.entities_parameters)
        else:
            resp = self.__send_request(PUT, "%s/%s/attrs/%s/%s" %
                        (V2_ENTITIES, self.entity_context[ENTITIES_ID], self.entity_context[ATTRIBUTES_NAME], value),
                        headers=self.headers, parameters=self.entities_parameters)

        # update self.entity_context with last values (ex: create request)
        for item in self.entity_context:
            if (self.entity_context[item] is None) or (self.entity_context[item] == "none"):
                if item not in (ATTRIBUTES_TYPE, METADATAS_TYPE):
                    self.entity_context[item] = self.dict_temp[item]
        return resp

    def update_an_attribute_by_id_and_by_name_in_raw_mode(self, context, entity_id, attribute_name, value=EMPTY):
        """
        update an attribute by ID and attribute name if it exists in raw mode
        :requests ->
                     value = False:  PUT  /v2/entities/<entity_id>/attrs/<attr_name>
                     value = True:   PUT  /v2/entities/<entity_id>/attrs/<attr_name>/value
        :payload --> Yes
        :query parameters --> Yes
        :param context: new context to update
        :param entity_id: entity id used to update
        :param attribute_name: attribute to update
        :param value: is used to modify only attribute value
        :return http response
        """
        attribute_str = EMPTY
        self.entity_context[ENTITIES_ID] = entity_id
        self.entity_context[ATTRIBUTES_NAME] = attribute_name
        self.entity_id_to_request = mapping_quotes(entity_id)  # used to verify if the entity returned is the expected

        # The same value from create request
        for item in self.entity_context:
            if self.entity_context[item] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.entity_context[item] = self.dict_temp[item]
        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)
        # elf.entity_id_to_request variable is used to verify if the entity returned is the expected
        self.entity_id_to_request = mapping_quotes(self.entity_context[ENTITIES_ID])

        # log entities contexts
        __logger__.debug("entity context to update by ID and by name in raw mode:")
        for item in self.entity_context:
            __logger__.debug("%s: %s" % (item, self.entity_context[item]))

        # create attributes with entity context
        if value == EMPTY:
            attribute_str = self.__create_attribute_by_id_attr_name_raw(self.entity_context)
        else:
            attribute_str = self.entity_context[ATTRIBUTES_VALUE]

        resp = self.__send_request(PUT, "%s/%s/attrs/%s/%s" % (V2_ENTITIES, self.entity_context[ENTITIES_ID],
                                                               self.entity_context[ATTRIBUTES_NAME], value),
                                   headers=self.headers, payload=attribute_str, parameters=self.entities_parameters)

        # update self.entity_context with last values (ex: create request)
        for item in self.entity_context:
            if (self.entity_context[item] is None)  or (self.entity_context[item] == "none"):
                if not (item in (ATTRIBUTES_TYPE, METADATAS_TYPE) and self.entity_context[item] is None):
                    self.entity_context[item] = self.dict_temp[item]
        return resp

    # delete entity
    def delete_entities_by_id(self, context, entity_id, attribute_name=None):
        """
        delete entities or attribute
        :request -> DELETE  /v2/entities/<entity_id>
                attribute_name == None:  DELETE  /v2/entities/<entity_id>
                attribute_name != None:  DELETE  /v2/entities/<entity_id>/attrs/<attr_name>
        :payload --> No
        :query parameters --> No
        :param entity_id: entity id used to delete
        :param attribute_name: attribute_name used to delete only one attribute, if it is None is not used.
        :return list
        """
        attribute_url = EMPTY

         # The same value from create request
        if entity_id != THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
            self.entity_context[ENTITIES_ID] = entity_id
        if attribute_name != THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
            self.entity_context[ATTRIBUTES_NAME] = attribute_name

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)

        self.entities_parameters.clear()
        if context.table is not None:
            for row in context.table:
                self.entities_parameters[row[PARAMETER]] = row[VALUE]

        # contexts and query parameter
        __logger__.debug("entity_id: %s" % self.entity_context[ENTITIES_ID])
        __logger__.debug("attribute_ name: %s" % self.entity_context[ATTRIBUTES_NAME])
        for item in self.entities_parameters:
            __logger__.debug("Queries parameters: %s=%s" % (item, self.entities_parameters[item]))

        if "type" in self.entities_parameters:
            self.entity_type_to_request = self.entities_parameters["type"]

        if attribute_name is not None:
            attribute_url = "/attrs/%s" % self.entity_context[ATTRIBUTES_NAME]
            # used to verify if the attribute deleted is the expected
            self.attribute_name_to_request = mapping_quotes(self.entity_context[ATTRIBUTES_NAME])


        # requests
        return self.__send_request(DELETE, "%s/%s%s" % (V2_ENTITIES, self.entity_context[ENTITIES_ID], attribute_url),
                                   headers=self.headers, parameters=self.entities_parameters)

        # ------- get CB values ------

    #  -----------  subscriptions -------------------

    def properties_to_subcription(self, context):
        """
        definition of properties to entities
          | parameter                      | value                   |
          | description                    | my first subscription   |
          | subject_type                   | room                    |
          | subject_id                     | room2                   |
          | subject_idPattern              | .*                      |
          | subject_entities_number        | 2                       |
          | subject_entities_suffix        | type                    |
          | condition_attrs                | temperature             |
          | condition_attrs_number         | 3                       |
          | condition_expression           | q>>>temperature>40      |
          | notification_http_url          | http://localhost:1234   |
          | notification_http_headers      | My-Header: activated    |
          | notification_http_qs           | options=myValues        |
          | notification_http_method       | My-Header: activated    |
          | notification_http_payload      | options=myValues        |
          | notification_attrs             | temperature             |
          | notification_attrs_number      | 3                       |
          | notification_attrsFormat       | options=keyValues       |
          | throttling                     | 5                       |
          | expires                        | 2016-04-05T14:00:00.00Z |
          | status                         | active                  |
        Hint: - If `subject_entities_number` is major than "1" will have N entities object using `subject_entities_prefix` to differentiate.
              - If `condition_attributes_number` is equal "1", the attribute name has not suffix, ex: `"attributes": ["temperature"]`
                else `condition_attributes_number` is major than "1" the attributes name are value plus a suffix (consecutive), ex:
                `"attributes": ["temperature", "temperature_0", "temperature_1", ..., "temperature_N"]`
              - If `notification_attributes_number` is equal "1", the attribute name has not suffix, ex: `"attributes": ["temperature"]`
                else `notification_attributes_number` is major than "1" the attributes name are value plus a suffix (consecutive), ex:
                `"attributes": ["temperature", "temperature_0", "temperature_1", ..., "temperature_N"]`
              - It is possible to use the same value of the previous request in another request using this string:
                  `the same value of the previous request`.
              - "type", "id", "attributes" could be random values.
                 The number after "=" is the number of chars
                     ex: | attributes_name | random=10 |
              - if we wanted an empty payload in a second request, use:
                      | parameter          |
                      | without_properties |
              - If would you like that `subject` field is missing, use `subject_type` equals to `without subject field`
              - If would you like that `entities` field is missing, use `subject_type` equals to `without entities field`
              - If would you like that `conditions` field is missing, use `condition_attributes` equals to `without condition field`
              - If would you like that `conditions attributes` field is empty, use `condition_attributes` equals to `array is empty`
              - If would you like that `conditions expression` field is empty, use `condition_expression` equals to `object is empty`
              - If would you like that `notification` field is missing, use `notification_callback` equals to `without notification field`
              - If would you like that `notification attributes` field is empty, use `notification_attributes` equals to `array is empty`
              - In expression value have multiples expressions uses `&` as separator, and in each operation use `>>>` as separator between the key and the value,
                 ex:
                     `| condition_expression | q>>>temperature>40&georel>>>near&geometry>>>point&coords>>>40.6391 |`
              - If notification_http_url has `replace_host` value, ex: http://replace_host:1234/notify, it string is replaced by the hostname (used to notifications).
        :param context: context variable with properties to entities
        """
        # store previous subsciption context dict temporally (used in update request)
        self.subsc_dict_temp = {}
        for item in self.subscription_context:
            self.subsc_dict_temp[item] = self.subscription_context[item]

        # store parameters in entities contexts
        self.__init_subscription_context_dict()  # reinit context dict (used in update request)
        if context.table is not None:
            for row in context.table:
                if row[PARAMETER] in self.subscription_context:
                    self.subscription_context[row[PARAMETER]] = row[VALUE]
                elif row[PARAMETER] == u'without_properties':
                    break
                else:
                    __logger__.warn("Wrong parameter: %s" % row[PARAMETER])

        # The same value from create request (used in update request)
        for item in self.subscription_context:
            if self.subscription_context[item] == THE_SAME_VALUE_OF_THE_PREVIOUS_REQUEST:
                self.subscription_context[item] = self.subsc_dict_temp[item]

        # replace_host (used in notifications)
        hostname = socket.gethostname()
        if self.subscription_context[NOTIFICATION_HTTP_URL].find(REPLACE_HOST) >= 0:
            self.subscription_context[NOTIFICATION_HTTP_URL] = self.subscription_context[NOTIFICATION_HTTP_URL].replace(REPLACE_HOST, "%s.hi.inet" % hostname)


        # Random values
        self.subscription_context = self.__random_values(RANDOM_SUBSCRIPTION_LABEL, self.subscription_context)
        if self.subscription_context[CONDITION_EXPRESSION] is not None and self.subscription_context[CONDITION_EXPRESSION].find(RANDOM) >= 0:   #  random condition expression
            exp_op = self.subscription_context[CONDITION_EXPRESSION].split("&")
            temp = EMPTY
            for op in exp_op:
                if op .find(RANDOM) >= 0:
                    exp_split = op.split(">>>")
                    op = "%s>>>%s" % (exp_split[0], string_generator(self.__get_random_number(exp_split[1])))
                temp = "%s%s&" % (temp, op)
            self.subscription_context[CONDITION_EXPRESSION] = temp[:-1]

        if self.subscription_context[CONDITION_ATTRS] is not None and self.subscription_context[CONDITION_ATTRS] != "array is empty" \
           and self.subscription_context[CONDITION_ATTRS_NUMBER] == 0:
            self.subscription_context[CONDITION_ATTRS_NUMBER] = 1
        if self.subscription_context[NOTIFICATION_ATTRS] is not None and self.subscription_context[NOTIFICATION_ATTRS] != "array is empty" \
           and self.subscription_context[NOTIFICATION_ATTRS_NUMBER] == 0:
            self.subscription_context[NOTIFICATION_ATTRS_NUMBER] = 1

        # log entities contexts
        __logger__.debug("subscription context properties:")
        for item in self.subscription_context:
            __logger__.debug("   - %s: %s" % (item, self.subscription_context[item]))

    def create_subscription(self):
        """
        create a subscription
        :request -> POST /v2/subscriptions/
        :payload --> Yes
        :query parameters --> No
        :return responses
        """
        csub = {}
        if self.subscription_context[DESCRIPTION] != u'without payload':
            # create description field
            if self.subscription_context[DESCRIPTION] is not None:
                csub[DESCRIPTION] = self.subscription_context[DESCRIPTION]
            # create subject field and sub-fields
            if self.subscription_context[SUBJECT_TYPE] !=  u'without subject field':
                csub["subject"] = {}
                if self.subscription_context[SUBJECT_TYPE] != u'without entities field':
                    entities = self.__create_subsc_entities(self.subscription_context)
                    csub["subject"]["entities"] = entities
                if self.subscription_context[CONDITION_ATTRS] != u'without condition field':
                    condition = self.__create_subsc_condition(self.subscription_context)
                    csub["subject"]["condition"] = condition

            # create notification field and sub-fields
            if self.subscription_context[NOTIFICATION_HTTP_URL] != u'without notification field':
                notification = self.__create_subsc_notification(self.subscription_context)
                csub["notification"] = notification

            # create throttling field
            if self.subscription_context[THROTTLING] != 0:
                csub["throttling"] = int(self.subscription_context[THROTTLING])

            # create expires field
            if self.subscription_context[EXPIRES] is not None:
                csub["expires"] = self.subscription_context[EXPIRES]

            # create status field
            if self.subscription_context[STATUS] is not None:
                csub["status"] = self.subscription_context[STATUS]

        # request
        __logger__.debug("subscription: %s" % str(csub))
        payload = convert_dict_to_str(csub, JSON)
        if csub != {}:
            resp = self.__send_request(POST, V2_SUBSCRIPTIONS, headers=self.headers, payload=payload,
                                       parameters=self.entities_parameters)
        else:
            resp = self.__send_request(POST, V2_SUBSCRIPTIONS, parameters=self.entities_parameters,
                                       headers=self.headers)
        return  resp

    def create_subscription_in_raw_mode(self):
        """
        create a subscription in raw mode
        :request -> POST /v2/subscriptions/
        :payload --> Yes
        :query parameters --> No
        :return responses
        """
        payload = "{"
        # description field
        if self.subscription_context[DESCRIPTION] is not None:
            payload = u'%s "description": %s,' % (payload, self.subscription_context[DESCRIPTION])

        # subject fields
        payload = u'%s %s,' % (payload, self.__create_subsc_subject_raw(self.subscription_context))

        # notification fields
        payload = u'%s %s,' % (payload, self.__create_subsc_notification_raw(self.subscription_context))

        # expires field
        if self.subscription_context[EXPIRES] is not None:
            payload = u'%s "expires": %s,' % (payload, self.subscription_context[EXPIRES])

        # status field
        if self.subscription_context[STATUS] is not None:
            payload = u'%s "status": %s,' % (payload, self.subscription_context[STATUS])

       # throttling field
        if self.subscription_context[THROTTLING] is not None:
            payload =  u'%s "throttling": %s,'  % (payload, self.subscription_context[THROTTLING])

        # payload
        payload = "%s }" % payload[:-1]
        __logger__.debug("subscription: %s" % payload)
        resp = self.__send_request(POST, V2_SUBSCRIPTIONS, headers=self.headers, payload=payload,
                                   parameters=self.entities_parameters)
        return resp

    # get subcriptions
    def get_subscription_by_id(self, subscription_id):
        """
        get subscription by id
        :request -> GET /v2/subscriptions/<subc_id>
        :payload --> No
        :query parameters --> No
        Hint: If you do like to use the subscriptionId of the subscription created previously, use `previous subs` value
        :return responses
        """
        __logger__.info("subscriptionId: %s" % subscription_id)
        return self.__send_request(GET, "%s/%s" % (V2_SUBSCRIPTIONS, subscription_id),headers=self.headers)


    #  --------- Fuctions that return values from library ---------

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

    def get_entity_context(self):
        """
        get entities contexts
        :return dict (see "constructor" method by dict fields)
        """
        return self.entity_context

    def get_entities_prefix(self):
        """
        get dict with if entity id or entity type are used as prefix
        :return: dict
        """
        return self.prefixes

    def get_entity_id_to_request(self):
        """
        return entity id used in request to get an entity
        used to verify if the entity returned is the expected
        :return string
        """
        return self.entity_id_to_request

    def get_entity_type_to_request(self):
        """
        return entity type used in request to get/delete an entity
        used to verify if the entity returned is the expected
        :return string
        """
        return self.entity_type_to_request

    def get_attribute_name_to_request(self):
        """
        return attribute name used in request to get an attribute
        used to verify if the attribute returned is the expected
        :return string
        """
        return self.attribute_name_to_request

    def get_subscription_context(self):
        """
        get subscription contexts
        :return dict (see "constructor" method by dict fields)
        """
        return self.subscription_context

    def get_request_response_string(self):
        """
        return a string with request and another one to response
        """
        return self.request_string, self.response_string
