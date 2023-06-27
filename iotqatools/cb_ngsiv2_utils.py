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

__author__ = 'Manu'

import requests
import json

from iotqatools.iot_logger import get_logger
from requests.exceptions import RequestException
from iotqatools.iot_tools import PqaTools
from helpers_utils import convert_str_to_list, remove_quote, string_generator, mapping_quotes

__logger__ = get_logger("CB Utils")

# Random values
RANDOM_ENTITIES_LABEL = ['attributes_name', 'attributes_value', 'attributes_type', 'metadatas_name', 'metadatas_value',
                         'metadatas_type', 'entities_id', 'entities_type']
RANDOM_SUBSCRIPTION_LABEL = ['subject_type', 'subject_id', 'subject_idPattern', 'condition_attrs', 'notification_attrs',
                             'notification_except_attrs', 'description']
RANDOM_QUERIES_PARAMETERS_LABELS = ["options"]

class CbNgsi10v2Utils(object):
    """
    Basic functionality for ContextBroker v2 API
    """

    def __init__(self, instance,
                 protocol="http",
                 port="1026",
                 path_entities="/v2/entities",
                 path_entities_id="/v2/entities/entityId",
                 path_entities_id_attrs="/v2/entities/entityId/attrs",
                 path_entities_id_attrs_attr="/v2/entities/entityId/attrs/attrName",
                 path_entities_id_attrs_attr_value="/v2/entities/entityId/attrs/attrName/value",
                 path_types="/v2/types",
                 path_types_type="/v2/types/entityType",
                 path_subscriptions="/v2/subscriptions",
                 path_subscriptions_id="/v2/subscriptions/subscriptionId",
                 path_batch_update="/v2/op/update",
                 path_batch_query="/v2/op/query",
                 path_statistics="/statistics",
                 path_version="/version",
                 log_instance=None,
                 log_verbosity='DEBUG',
                 default_headers={'Accept': 'application/json'},
                 verify=False,
                 check_json=True):
        """
        CB Utils constructor
        :param instance:
        :param protocol:
        :param port:
        :param path_entities:
        :param path_entities_id:
        :param path_entities_id_attrs:
        :param path_entities_id_attrs_attr:
        :param path_entities_id_attrs_attr_value:
        :param path_types:
        :param path_types_type:
        :param path_subscriptions:
        :param path_subscriptions_id:
        :param path_statistics:
        :param path_version:
        :param log_instance:
        :param log_verbosity:
        :param default_headers:
        :param verify: ssl check
        :param check_json:
        """
        # initialize logger
        if log_instance is not None:
            self.log = log_instance
        else:
            self.log = get_logger('CbNgsi10Utilsv2', log_verbosity)

        # Assign the values
        self.default_endpoint = "{}://{}:{}".format(protocol, instance, port)
        self.headers = default_headers
        self.path_entities = "{}{}".format(self.default_endpoint, path_entities)
        self.path_entities_id_attrs_attr = "{}{}".format(self.default_endpoint, path_entities_id_attrs_attr)
        self.path_delete_entity = "{}{}".format(self.default_endpoint, path_entities_id)
        self.path_statistics = path_statistics
        self.path_entities = "{}{}".format(self.default_endpoint, path_entities)
        self.path_types = "{}{}".format(self.default_endpoint, path_types)
        self.path_update_entity = "{}{}".format(self.default_endpoint, path_entities_id_attrs)
        self.path_get_entity_attrs = "{}{}".format(self.default_endpoint, path_entities_id_attrs)
        self.path_subscriptions = "{}{}".format(self.default_endpoint, path_subscriptions)
        self.path_subscriptions_by_id = "{}{}".format(self.default_endpoint, path_subscriptions_id)
        self.path_batch_update = "{}{}".format(self.default_endpoint, path_batch_update)
        self.path_batch_query = "{}{}".format(self.default_endpoint, path_batch_query)
        self.path_version = path_version
        self.verify = verify
        self.check_json = check_json

        # initialize context dictionaries
        self.entities_parameters = {}
        self.__init_entity_context_dict()
        self.__init_subscription_context_dict()
        self.__init_query_batch_properties_dict()
        self.previous_value = {'name': None, 'type': None, 'value': None}


    def __init_entity_context_dict(self):
        """
        initialize entity_context dict (used in create, update or append entity)
        """

        self.entity_context = {'entities_number': 1,
                               'entities_type': 'Thing',
                               'entities_id': None,
                               'entities_prefix': {'id': False, 'type': False},
                               'attributes_number': 0,
                               'attributes_name': None,
                               'attributes_value': None,
                               'attributes_type': 'none',
                               'attributes_metadata': 'true',
                               'metadatas_number': 0,
                               'metadatas_name': None,
                               'metadatas_type': 'none',
                               'metadatas_value': None}


    def __init_subscription_context_dict(self):
        """
        initialize subscription_context dict (used in create or update subcription)
        """
        self.subscription_context = {'description': None,
                                     'subject_type': None,
                                     'subject_id': None,
                                     'subject_idPattern': None,
                                     'subject_typePattern': None,
                                     'subject_entities_number': 1,
                                     'subject_entities_prefix': '', # allowed values(id | type)
                                     'condition_attrs': None,
                                     'condition_attrs_number': 0,
                                     'condition_expression': None,
                                     'notification_attrs': None,
                                     'notification_except_attrs': None,
                                     'notification_attrs_number': 0,
                                     'notification_attrsFormat': None,
                                     'notification_metadata': None,
                                     'notification_http_url': None,
                                     'notification_http_custom_url': None,
                                     'notification_http_custom_headers': None,
                                     'notification_http_custom_qs': None,
                                     'notification_http_custom_method': None,
                                     'notification_http_custom_payload': None,
                                     'throttling': None,
                                     'expires': None,
                                     'status': None}

    def __init_query_batch_properties_dict(self):
        """
        initialize query batch dict (used in query batch operations)
        """
        self.query_batch_dict = {}

    def __send_request(self, method, url, headers=None, payload=None, verify=None, query=None):
        """
        Send a request to a specific url in a specifying type of http request
        """

        parameters = {
            'method': method,
            'url': url,
        }

        if headers is not None:
            parameters.update({'headers': headers})

        if payload is not None:
            if self.check_json:
                parameters.update({'data': json.dumps(payload, ensure_ascii=False).encode('utf-8')})
            else:
                parameters.update({'data': payload})

        if query is not None:
            parameters.update({'params': query})

        if verify is not None:
            parameters.update({'verify': verify})
        else:
            # If the method does not include the verify parameter, it takes the value from object
            parameters.update({'verify': self.verify})

        # Send the requests
        try:
            response = requests.request(**parameters)
        except RequestException, e:
            PqaTools.log_requestAndResponse(url=url, headers=headers, params=query, data=payload, comp='CB',
                                            method=method)
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)

        # Log data
        PqaTools.log_fullRequest(comp='CB', response=response, params=parameters)

        return response

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
                    meta_dict[name]['value'] = metadata_value
                if metadata_type != 'none':
                    meta_dict[name]['type'] = metadata_type
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
        if int(entity_context['metadatas_number']) > 0:
            metadata = self.__create_metadata(entity_context['metadatas_number'], entity_context['metadatas_name'],
                                              entity_context['metadatas_type'], entity_context['metadatas_value'])
        __logger__.debug("Metadatas: %s" % str(metadata))

        # create attributes
        if mode == 'normalized':
            if metadata != {}:
                attr['metadata'] = metadata
            if entity_context['attributes_type'] != "none":
                attr['type'] = entity_context['attributes_type']
            if entity_context['attributes_value'] is not None:
                attr['value'] = entity_context['attributes_value']
        elif mode == 'keyValues':
            if entity_context['attributes_value'] is not None:
                attr = entity_context['attributes_value']

        if entity_context['attributes_name'] is not None:
            for i in range(int(entity_context['attributes_number'])):
                if int(entity_context['attributes_number']) > 1:
                    name = "%s_%s" % (entity_context['attributes_name'], str(i))
                else:
                    name = entity_context['attributes_name']
                attributes[name] = attr
        return attributes


    def __create_attribute_raw(self, entity_context, mode):
        """
        create an attribute with entity context in raw mode
        :return (string)
        Hint: to create N attributes use & as separator. Ev:
                  | parameter           | value                                 |
                  | entities_type       | "house"                               |
                  | entities_id         | "room_2"                              |
                  | attributes_name     | "temperature"&"pressure"&"humidity"   |
                  | attributes_value    | 34&"high"&"random=3"                  |
                  | attributes_type     | "celsius"&&"porcent"                  |
                  | attributes_metadata | true&false                            |
                  | metadatas_name      | "very_hot"                            |
                  | metadatas_type      | "alarm"                               |
                  | metadatas_value     | "default"                             |
        """
        attributes_final = ''
        separator = "&"
        name_list = []
        values_list = []
        type_list = []
        meta_names_list = []
        meta_values_list = []
        meta_types_list = []
        # create N attributes with/without attribute type and metadatas (with/without type)
        if entity_context['attributes_name'] is not None:
            name_list = convert_str_to_list(entity_context['attributes_name'], separator)
        if entity_context['attributes_value'] is not None:
            values_list = convert_str_to_list(entity_context['attributes_value'], separator)
        if entity_context['attributes_type'] is not None:
            while entity_context['attributes_type'].find("&&") >= 0:
                entity_context['attributes_type'] = entity_context['attributes_type'].replace("%s%s" % (separator, separator), '%s"none"%s' % (separator, separator))
            type_list = convert_str_to_list(entity_context['attributes_type'], separator)
        if entity_context['metadatas_name'] is not None:
            meta_names_list = convert_str_to_list(entity_context['metadatas_name'], separator)
        if entity_context['metadatas_value'] is not None:
            meta_values_list = convert_str_to_list(entity_context['metadatas_value'], separator)
        if entity_context['metadatas_type'] is not None:
            while entity_context['metadatas_type'].find("&&") >= 0:
                entity_context['metadatas_type'] = entity_context['metadatas_type'].replace("%s%s" % (separator, separator), '%s"none"%s' % (separator, separator))
            meta_types_list = convert_str_to_list(entity_context['metadatas_type'], separator)

        for pos in range(len(name_list)):
            attribute_str = ''
            # create a entity with N attributes in normalized mode
            if mode == 'normalized':
                # append attribute type if it does exist
                if (len(type_list) > pos) and (remove_quote(type_list[pos]) != 'none'):
                    attribute_str = '"type": %s' % type_list[pos]

                # append metadata if it does exist
                if (len(meta_names_list) > pos) and meta_names_list[pos] != None:
                    if (len(meta_types_list) > pos) and remove_quote(meta_types_list[pos]) != 'none':
                        metadata = '"metadata": {%s: {"value": %s, "type": %s}}' % (meta_names_list[pos],
                                                                                    meta_values_list[pos],
                                                                                    meta_types_list[pos])
                    else:
                        metadata = '"metadata": {%s: {"value": %s}}' % (meta_names_list[pos],
                                                                        meta_values_list[pos])
                    if attribute_str != '':
                        attribute_str = '%s, %s' % (attribute_str, metadata)
                    else:
                        attribute_str = metadata

                # append attribute value if it exist
                if values_list[pos] is not None:
                    if attribute_str != '':
                        attribute_str = '%s, "value": %s' % (attribute_str, values_list[pos])
                    else:
                        attribute_str = '"value": %s' % values_list[pos]

                # append attribute name
                if name_list[pos] is not None:
                    attribute_str = u'%s:{%s},' % (name_list[pos], attribute_str)
                attributes_final = "%s %s" % (attributes_final, attribute_str)

            # create a entity with N attributes in keyValues mode
            elif mode == 'keyValues' and entity_context['attributes_name'] is not None:
                attribute_str = u'%s: %s,' % (name_list[pos], values_list[pos])
                attributes_final = "%s %s" % (attributes_final, attribute_str)

        __logger__.debug("Atribute with raw values: %s" % attributes_final[:-1])
        return attributes_final[:-1]


    def __create_subsc_subject_raw(self, subscription_context):
        """
        create subject field (entities and condition) to subscriptions in raw mode
        :return string
        """
        # entities fields
        entities = u'"entities": [{'
        # type or typePattern field
        if subscription_context['subject_type'] is not None:
            entities = u'%s"type": %s,' % (entities, subscription_context['subject_type'])
        elif subscription_context['subject_typePattern'] is not None:
            entities = u'%s"typePattern": %s,' % (entities, subscription_context['subject_typePattern'])
        # id or idPattern field
        if subscription_context['subject_id'] is not None:
            entities = u'%s"id": %s}],' % (entities, subscription_context['subject_id'])
        elif subscription_context['subject_idPattern'] is not None:
            entities = u'%s"idPattern": %s}],' % (entities, subscription_context['subject_idPattern'])

        # condition fields
        condition = u'"condition": {'
        # attributes field
        if subscription_context['condition_attrs'] is not None:
            if remove_quote(subscription_context['condition_attrs']) == "array is empty":
                subscription_context['condition_attrs'] = ''
            condition = u'%s "attrs": [%s]' % (condition, subscription_context['condition_attrs'])
            if subscription_context['condition_expression'] is not None:
                condition = "%s," % condition
        # expression field
        if subscription_context['condition_expression'] is not None:
            exp_op = subscription_context['condition_expression'].split("&")
            internal_conditions = ''
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
        url = ''
        attributes = ''
        throttling = ''
        headers = ''
        query = ''
        attrsFormat = ''
        notification = ''
        http_custom_field_exist = False
        http_custom = 'httpCustom'
        # http url field
        if subscription_context['notification_http_url'] is not None:
            notification = u'"http": { "url": %s,' % (subscription_context['notification_http_url'])

        ## httpCustom fields
        # httpCustom url field
        if subscription_context['notification_http_custom_url'] is not None:
            if not http_custom_field_exist:
                http_custom_field_exist = True  # used to determine whether httpCustom dict is created or not
                #notification = u'"%s": {' % http_custom
            notification = u'"%s": { "url": %s,' % (http_custom, subscription_context['notification_http_custom_url'])
        # httpCustom headers field
        if subscription_context['notification_http_custom_headers'] is not None:
            if not http_custom_field_exist:
                http_custom_field_exist = True  # used to determine whether httpCustom dict is created or not
                notification = u'"%s": {' % http_custom
            notification = u'%s "headers": %s,' % (notification, subscription_context['notification_http_custom_headers'])
        # httpCustom qs field
        if subscription_context['notification_http_custom_qs'] is not None:
            if not http_custom_field_exist:
                http_custom_field_exist = True  # used to determine whether httpCustom dict is created or not
                notification = u'"%s": {' % http_custom
            notification = u'%s "qs": %s,' % (notification, subscription_context['notification_http_custom_qs'])
       # httpCustom method field
        if subscription_context['notification_http_custom_method'] is not None:
            if not http_custom_field_exist:
                http_custom_field_exist = True  # used to determine whether httpCustom dict is created or not
                notification = u'"%s": {' % http_custom
            notification = u'%s "method": %s,' % (notification, subscription_context['notification_http_custom_method'])
        # httpCustom payload field
        if subscription_context['notification_http_custom_payload'] is not None:
            if not http_custom_field_exist:
                http_custom_field_exist = True  # used to determine whether httpCustom dict is created or not
                notification = u'"%s": {' % http_custom
            notification = u'%s "payload": %s,' % (notification, subscription_context['notification_http_custom_payload'])
        if notification != '':
            notification = u'%s},' % notification[:-1]

        # attrsFormat field
        if subscription_context['notification_attrsFormat'] is not None:
            attrsFormat = u'"attrsFormat": %s,' % subscription_context['notification_attrsFormat']
            notification = "%s %s" % (notification, attrsFormat)

        # attributes field
        if subscription_context['notification_attrs'] is not None:
            attributes = u'"attrs": [%s],' % (subscription_context['notification_attrs'])
            notification = "%s %s" % (notification, attributes)

        # exceptAttributes field
        if subscription_context['notification_except_attrs'] is not None:
            attributes = u'"exceptAttrs": [%s],' % (subscription_context['notification_except_attrs'])
            notification = "%s %s" % (notification, attributes)

        # metadata field
        if subscription_context['notification_metadata'] is not None:
            metadata = u'"metadata": %s,' % (subscription_context['notification_metadata'])
            notification = "%s %s" % (notification, metadata)

        if notification != '':
            notification = u'{%s}' % notification[:-1]

        return u'"notification": %s' % notification


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
                if (dictionary[random_label] is not None) and (dictionary[random_label].find('random') >= 0):
                    temp = dictionary[random_label].split(u'random=')
                    label_final = ''
                    for pos in range(len(temp)-1):
                        rn = self.__get_random_number(temp[pos+1])
                        label_final = string_generator(rn) + temp[pos+1][rn:]
                        rns = str(rn)
                    if temp[-1] != rns:  # used mainly with values with quotes
                        label_final = "%s%s" % (label_final, temp[-1][len(rns):])
                    dictionary[random_label] = "%s%s" % (temp[0], label_final)
        return dictionary


    @staticmethod
    def __get_random_number(label):
        """
        get random number
        :param label: ex: random=10 return: 10
        :return int
        """
        number = u'0123456789'
        c = 0
        length = len(label)-1
        while (length >= c) and (label[c] in number):
            c=c+1
        return int(label[:c])


    def set_service(self, service):
        self.headers['Fiware-Service'] = service

    def set_subservice(self, subservice):
        if subservice != "None" and subservice != "none" and subservice != None:
            self.headers['Fiware-Servicepath'] = subservice

    def set_auth_token(self, auth_token):
        self.headers['X-Auth-Token'] = auth_token

    def remove_content_type_header(self):
        """
        This method is used when sending get or delete actions through pep
        Yes, I know this is not the more suitable way to do that, but probably is the less disruptive way
        :return: True if header has been removed | False if header has not been removed
        """
        if 'content-type' in self.headers:
            del self.headers['content-type']
            return True
        else:
            return False

    def append_new_header(self, header, value):
        self.headers[header] = value

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
        header_temp = {}
        for item in self.headers:
            header_temp[item] = self.headers[item]
        if prev.lower() != 'true':
            self.headers.clear()
        for row in context.table:
            if row['value'] == "the same value of the previous request":
                self.headers[row['parameter']] = header_temp[row['parameter']]
            else:
                self.headers[row['parameter']] = row['value']


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
        if context.table is not None:
            for row in context.table:
                self.headers[row['parameter']] = row['value']

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
              - if "attr_value" has "timestamp in last minutes" as value is generate a timestamp with N last minutes of current timestamp
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
                if row['parameter'] in self.entity_context:
                    self.entity_context[row['parameter']] = row['value']
                elif row['parameter'] == u'without_properties':
                    break
                elif row['parameter'].find("qp_") >= 0:
                    qp = str(row['parameter']).split("qp_")[1]
                    self.entities_parameters[qp] = row['value']
                else:
                    __logger__.warn("Wrong parameter: %s" % row['parameter'])

        # The same value from create request (used in update request)
        for item in self.entity_context:
            if self.entity_context[item] == 'the same value of the previous request':
                self.entity_context[item] = self.dict_temp[item]

        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)
        self.entities_parameters = self.__random_values(RANDOM_QUERIES_PARAMETERS_LABELS, self.entities_parameters)

        # timestamp on last minutes ex: "timestamp in last minutes=20"
        if (self.entity_context['attributes_value'] is not None) and (self.entity_context['attributes_value'].find("timestamp in last minutes") >= 0):
            ts_split = remove_quote(self.entity_context['attributes_value']).split("=")
            last_minutes = int(ts_split[1])*60
            self.entity_context['attributes_value'] = '"%s"' % generate_date_zulu(generate_timestamp() - last_minutes)

        if self.entity_context['attributes_name'] is not None and self.entity_context['attributes_number'] == 0:
            self.entity_context['attributes_number'] = 1
        if self.entity_context['metadatas_name'] is not None and self.entity_context['metadatas_number'] == 0:
            self.entity_context['metadatas_number'] = 1

        # log entities contexts
        __logger__.debug("entity context properties:")
        for item in self.entity_context:
            __logger__.debug("   - %s: %s" % (item, self.entity_context[item]))

        # log entities_parameters
        __logger__.debug("queries parameters:")
        for item in self.entities_parameters:
            __logger__.debug("   - %s: %s" % (item, self.entities_parameters[item]))

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
        entity = ''
        attribute_str = ''
        self.entity_context['entities_number'] = 1
        self.entity_context['attributes_number'] = 1

        # create attribute with/without attribute type and metadatas (with/without type)
        attribute_str = self.__create_attribute_raw(self.entity_context, mode)

        # if options=keyValues the attribute values is all. Attribute_type and metadata(s) are restarted
        if 'options' in self.entities_parameters and self.entities_parameters['options'] == 'keyValues':
            key_value_attr = attribute_str.split(":")[1]
            self.entity_context['attributes_value'] = key_value_attr
            self.entity_context['attributes_type'] = 'none'
            self.entity_context['metadatas_number'] = 0
            self.entity_context['metadatas_name'] = None

        # create entity with attribute value in raw
        if self.entity_context['entities_type'] != 'Thing':
            entity = '"type": %s' % self.entity_context['entities_type']
        if self.entity_context['entities_id'] is not None:
            if entity != '':
                entity = '%s, "id": %s' % (entity, self.entity_context['entities_id'])
            else:
                entity = '"id": %s' % self.entity_context['entities_id']
        if attribute_str != '':
            payload = u'{%s, %s}' % (entity, attribute_str)
        else:
            payload = u'{%s}' % entity

        resp = self.__send_request('post', self.path_entities, headers=self.headers, payload=json.loads(payload),
                                   query=self.entities_parameters)
        self.action_type = 'append'
        return resp


    def get_entity_context(self):
        """
        get entities contexts
        :return dict (see "constructor" method by dict fields)
        """
        return self.entity_context

    def get_action_type(self):
        """
        get action type, used to notification special metadata "actionType"
        """
        return self.action_type

    def get_previous_value(self):
        """
        get previous value and previous type in the attributes before the update, used to notification special metadata "previousValue". Ex:
        self.previous_value = {"name": None,
                               "type": None,
                               "value": None}
        """
        return self.previous_value

    def get_entities_parameters(self):
        """
        return queries parameters used in list entities
        :return: dict
        """
        return self.entities_parameters

    def properties_to_subcription(self, context, listener_host, listener_port, listener_port_https, cep_url):
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
        :param listener_host: listener host from properties.json
        :param listener_port: listener port from properties.json
        :param listener_port_https: listener port https from properties.json
        :param cep_url: used to replace CEP used as notify_url
        """
        # store previous subsciption context dict temporally (used in update request)
        self.subsc_dict_temp = {}
        for item in self.subscription_context:
            self.subsc_dict_temp[item] = self.subscription_context[item]

        # store parameters in entities contexts
        self.__init_subscription_context_dict()  # reinit context dict (used in update request)
        if context.table is not None:
            for row in context.table:
                if row['parameter'] in self.subscription_context:
                    self.subscription_context[row['parameter']] = row['value']
                elif row['parameter'] == u'without_properties':
                    break
                else:
                    __logger__.warn("Wrong parameter: %s" % row['parameter'])

        # The same value from create request (used in update request)
        for item in self.subscription_context:
            if self.subscription_context[item] == 'the same value of the previous request':
                self.subscription_context[item] = self.subsc_dict_temp[item]

        # replace_host string in url is replaced to the listener property (used in notification field)
        if (self.subscription_context['notification_http_url'] is not None) and (
                self.subscription_context['notification_http_url'].find('replace_host') >= 0):
            self.subscription_context['notification_http_url'] = self.subscription_context['notification_http_url'].replace(
                'replace_host', listener_host)
        if (self.subscription_context['notification_http_custom_url'] is not None) and (
                self.subscription_context['notification_http_custom_url'].find('replace_host') >= 0):
            self.subscription_context['notification_http_custom_url'] = self.subscription_context[
                'notification_http_custom_url'].replace('replace_host', listener_host)

        # replace_port string in url is replaced to the listener property (used in notification field)
        if (self.subscription_context['notification_http_url'] is not None) and (
                self.subscription_context['notification_http_url'].find('replace_port') >= 0):
            self.subscription_context['notification_http_url'] = self.subscription_context['notification_http_url'].replace(
                'replace_port', listener_port)
        if (self.subscription_context['notification_http_custom_url'] is not None) and (
                self.subscription_context['notification_http_custom_url'].find('replace_port') >= 0):
            self.subscription_context['notification_http_custom_url'] = self.subscription_context[
                'notification_http_custom_url'].replace('replace_port', listener_port)

        # replace_https_port string in url is replaced to the listener property (used in notification field)
        if (self.subscription_context['notification_http_url'] is not None) and (
                self.subscription_context['notification_http_url'].find('replace_https_port') >= 0):
            self.subscription_context['notification_http_url'] = self.subscription_context['notification_http_url'].replace(
                'replace_https_port', listener_port_https)
        if (self.subscription_context['notification_http_custom_url'] is not None) and (
                self.subscription_context['notification_http_custom_url'].find('replace_https_port') >= 0):
            self.subscription_context['notification_http_custom_url'] = self.subscription_context[
                'notification_http_custom_url'].replace('replace_https_port', listener_port_https)

        # CEP url replacement
        if (self.subscription_context['notification_http_url']) == 'CEP':
            self.subscription_context['notification_http_url'] = '"' + cep_url + '"'
        if (self.subscription_context['notification_http_custom_url']) == 'CEP':
            self.subscription_context['notification_http_custom_url'] = '"' + cep_url + '"'

        # Random values
        self.subscription_context = self.__random_values(RANDOM_SUBSCRIPTION_LABEL, self.subscription_context)
        if self.subscription_context['condition_expression'] is not None and self.subscription_context[
            'condition_expression'].find('random') >= 0:  # random condition expression
            exp_op = self.subscription_context['condition_expression'].split(
                "&")  # ex: ["q>>>random=10", "georel>>>near;minDistance:5000", "geometry>>><geometry>", "coords>>>25.774,-80.190"]
            temp = ''
            for op in exp_op:
                if op.find('random') >= 0:
                    exp_split = op.split(">>>")  # ex: ["q>", "random=10"]
                    rnd_split = exp_split[1].split("=")  # ex: ["random", "10"]
                    op = "%s>>>%s" % (exp_split[0], string_generator(self.__get_random_number(rnd_split[1])))
                temp = "%s%s&" % (temp, op)
            self.subscription_context['condition_expression'] = temp[:-1]

        if self.subscription_context['condition_attrs'] is not None and self.subscription_context[
            'condition_attrs'] != "array is empty" \
                and self.subscription_context['condition_attrs_number'] == 0:
            self.subscription_context['condition_attrs_number'] = 1
        if self.subscription_context['notification_attrs'] is not None and self.subscription_context[
            'notification_attrs'] != "array is empty" \
                and self.subscription_context['notification_attrs_number'] == 0:
            self.subscription_context['notification_attrs_number'] = 1
        if self.subscription_context['notification_except_attrs'] is not None and self.subscription_context[
            'notification_except_attrs'] != "array is empty" \
                and self.subscription_context['notification_attrs_number'] == 0:
            self.subscription_context['notification_attrs_number'] = 1

        # log entities contexts
        __logger__.debug("subscription context properties:")
        for item in self.subscription_context:
            __logger__.debug("   - %s: %s" % (item, self.subscription_context[item]))

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
        if self.subscription_context['description'] is not None:
            payload = u'%s "description": %s,' % (payload, self.subscription_context['description'])

        # subject fields
        payload = u'%s %s,' % (payload, self.__create_subsc_subject_raw(self.subscription_context))

        # notification fields
        payload = u'%s %s,' % (payload, self.__create_subsc_notification_raw(self.subscription_context))

        # expires field
        if self.subscription_context['expires'] is not None:
            payload = u'%s "expires": %s,' % (payload, self.subscription_context['expires'])

        # status field
        if self.subscription_context['status'] is not None:
            payload = u'%s "status": %s,' % (payload, self.subscription_context['status'])

       # throttling field
        if self.subscription_context['throttling'] is not None:
            payload =  u'%s "throttling": %s,'  % (payload, self.subscription_context['throttling'])

        # payload
        payload = "%s }" % payload[:-1]
        __logger__.debug("subscription: %s" % payload)
        resp = self.__send_request('post', self.path_subscriptions, headers=self.headers, payload=json.loads(payload),
                                   query=self.entities_parameters)
        return resp

    def update_or_append_an_attribute_by_id(self, method, entity_id, mode):
        """
        update or append an attribute by id
        :request -> /v2/entities/<entity_id>
        :payload --> Yes
        :query parameters --> Yes
        :param method: method used in request (POST, PATCH, PUT)
        :param entity_id: entity used to update or append
        :param mode: mode in that will be created attributes in request ( normalized | keyValues | values)
        Hint: if would like a query parameter name, use `qp_` prefix
        :return http response
        """
        self.entity_context['entities_id'] = entity_id
        # The same value from create request
        for item in self.entity_context:
            if self.entity_context['entities_id'] == 'the same value of the previous request':
                self.entity_context['entities_id'] = self.dict_temp['entities_id']
        self.entity_id_to_request = mapping_quotes(
            self.entity_context['entities_id'])  # used to verify if the entity returned is the expected

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)

        # create attributes with entity context
        entities = self.__create_attributes(self.entity_context, mode)

        path = self.path_update_entity.replace('entityId', self.entity_context['entities_id'])

        # FIXME: it doesn't make sense to send this operation without payload...
        if entities != {}:
            resp = self.__send_request(method, path, headers=self.headers, payload=entities, query=self.entities_parameters)
        else:
            resp = self.__send_request(method, path, headers=self.headers, query=self.entities_parameters)
        # update self.entity_context with last values (ex: create request)
        for item in self.entity_context:
            if (self.entity_context[item] is None) or (self.entity_context[item] == 'none') or (
                    self.entity_context[item] == 'Thing'):
                if item not in ('attributes_type', 'metadatas_type', 'attributes_value'):
                    self.entity_context[item] = self.dict_temp[item]

        # if options=keyValues is used, the type and metadatas are not used
        if 'options' in self.entities_parameters and self.entities_parameters['options'] == 'keyValues':
            self.entity_context['attributes_type'] = 'none'
            self.entity_context['metadatas_number'] = 0
        if method == 'post':
            if self.entity_context['attributes_name'] != self.dict_temp['attributes_name'] or self.entity_context[
                'attributes_number'] != self.dict_temp['attributes_number']:
                self.action_type = 'append'
            else:
                self.action_type = 'update'
        else:
            self.action_type = 'update'
        self.previous_value['name'] = self.dict_temp['attributes_name']
        self.previous_value['value'] = self.dict_temp['attributes_value']
        self.previous_value['type'] = self.dict_temp['attributes_type']
        return resp

    def get_subscription_context(self):
        """
        get subscription contexts
        :return dict (see "constructor" method by dict fields)
        """
        return self.subscription_context

    def batch_op_entities_properties(self, entities):
        """
        define a entity to update in a single batch operations
        :param entities: entities properties to append
        :return dict (prpperties to update batch op)
        """
        entity_dict = {}
        self.__init_entity_context_dict()

        for item in entities:
            if item in self.entity_context:
                self.entity_context[item] = entities[item]

            # entity prefixes
            PREFIX_STR = u'entities_prefix_'
            ent_prefix = []
            if item.find(PREFIX_STR) >= 0:
                ent_prefix = item.split(PREFIX_STR)
                self.entity_context['entities_prefix'][ent_prefix[1]] = entities[item]

        # The same value from create request (used in update request)
        for item in self.entity_context:
            if self.entity_context[item] == 'the same value of the previous request':
                self.entity_context[item] = self.dict_temp[item]

        # Random values
        self.entity_context = self.__random_values(RANDOM_ENTITIES_LABEL, self.entity_context)

        if self.entity_context['attributes_name'] is not None and self.entity_context['attributes_number'] == 0:
            self.entity_context['attributes_number'] = 1
        if self.entity_context['metadatas_name'] is not None and self.entity_context['metadatas_number'] == 0:
            self.entity_context['metadatas_number'] = 1

        __logger__.debug("entity properties:")
        for e in self.entity_context:
            __logger__.debug("%s: %s" % (e, self.entity_context[e]))
        return self.entity_context

    def batch_update_in_raw(self, parameters, accumulate, op):
        """
        allows to create, update and/or delete several entities in a single batch operation in raw mode
        used mainly with data type as boolean, dict, list, null, numeric, etc
        :request -> POST /v2/op/update
        :payload --> Yes
        :query parameters --> Yes
        :param parameters: queries parameters
        :param op: specify the kind of update action to do (APPEND, APPEND_STRICT, UPDATE, DELETE)
        :param accumulate: entities accumulate with different properties
        :return http response
        """
        entity = '"entities": ['
        self.entities_parameters = parameters
        mode = 'normalized'

        if 'options' in self.entities_parameters:
            mode = self.entities_parameters['options']

        for item in accumulate:
            # create attributes from entity context in raw mode
            attributes = self.__create_attribute_raw(item, mode)
            # create entity in raw mode
            if item['entities_type'] != 'Thing':
                entity = '%s {"type": %s' % (entity, item['entities_type'])
            if item['entities_id'] is not None:
                if item['entities_type'] != 'Thing':
                    entity = '%s, "id": %s' % (entity, item['entities_id'])
                else:
                    entity = '%s {"id": %s' % (entity, item['entities_id'])
            if attributes != '':
                entity = u'%s, %s},' % (entity, attributes)
            else:
                entity = u'%s},' % entity

        payload = u'{"actionType": "%s", %s]}' % (mapping_quotes(op), entity[:-1]) # mapping_quote from helpers_utils.py
        __logger__.debug("payload: %s" % payload)

        resp = self.__send_request('post', self.path_batch_update, headers=self.headers, query=self.entities_parameters, payload=json.loads(payload))
        return resp

    def batch_query(self, parameters):
        """
        returns an Array containing one object per matching entity
        :request -> POST /v2/op/query
        :payload --> Yes
        :query parameters --> Yes
        :param parameters: queries parameters
        :return http response
        """
        self.entities_parameters = parameters

        # FIXME: it doesn't make sense to send this operation without payload...
        if self.query_batch_dict != {}:
            resp = self.__send_request('post', self.path_batch_query, headers=self.headers, query=self.entities_parameters, payload=self.query_batch_dict)
        else:
            resp = self.__send_request('post', self.path_batch_query, query=self.entities_parameters, headers=self.headers)
        return resp

    def version(self):
        """
        Get CB version
        """
        url = self.default_endpoint + self.path_version

        # send the request for the subscription
        response = self.__send_request('get', url, self.headers)
        return response

    def statistics(self):
        """
        Get CB statistics
        """
        url = self.default_endpoint + self.path_statistics

        # send the request for the subscription
        response = self.__send_request('get', url, self.headers)
        return response

    def create_entity(self, payload, headers={}, params=None):
        """
        Create a entity in ContextBroker with the standard entity creation
        :param payload: the payload
        :param headers: headers for the requests (fiware-service, fiware-servic-path and x-auth-token)
        :param params: params of the query if applicable
        The payload has to be like:
            {
              "type": "Room",
              "id": "Bcn-Welt",
              "temperature": {
                "value": 21.7
              },
              "humidity": {
                "value": 60
              },
              "location": {
                "value": "41.3763726, 2.1864475",
                "type": "geo:point",
                "metadata": {
                  "crs": {
                    "value": "WGS84"
                  }
                }
              }
            }
        """
        headers.update(self.headers)
        headers.update({'content-type': 'application/json'})
        return self.__send_request('post', self.path_entities, payload=payload, headers=headers, query=params,
                                   verify=None)

    def update_entity(self, payload, entity_id, headers={}, params=None):
        """
        Update a entity in ContextBroker with the standard entity creation
        :param payload: the payload
        :param headers: headers for the requests (fiware-service, fiware-servic-path and x-auth-token)
        :param params: params of the query if applicable
        The payload has to be like:
            {
              "temperature": {
                "value": 21.7
              },
              "humidity": {
                "value": 60
              },
              "location": {
                "value": "41.3763726, 2.1864475",
                "type": "geo:point",
                "metadata": {
                  "crs": {
                    "value": "WGS84"
                  }
                }
              }
            }
        """
        headers.update(self.headers)
        headers.update({'content-type': 'application/json'})

        path = self.path_update_entity.replace('entityId', entity_id)

        return self.__send_request('post', path, payload=payload, headers=headers, query=params,
                                   verify=None)

    def get_entity_types(self, headers={}, params=None):
        """
        GET /v2/types
        """

        # Add default headers to the request
        headers.update(self.headers)

        # Store params to be used in other steps after the one using this function
        self.entities_parameters = params

        path = self.path_entities

        return self.__send_request('get', self.path_types, headers=headers, verify=None, query=params)

    def list_entities(self, headers={}, params=None):
        """
        Retrieves a list of entities which match different criteria (by id, idPattern, type or those which match a
        query or geographical query)
        :param headers:
        :param filters:
        :rtype : object
        :
        """

        # Add default headers to the request
        headers.update(self.headers)

        # Store params to be used in other steps after the one using this function
        self.entities_parameters = params

        return self.__send_request('get', self.path_entities, headers=headers, verify=None, query=params)

    def get_entity_attrs(self, entity_id, headers={}, params=None):
        """
        GET /v2/entities/{id}/attrs
        """

        # Add default headers to the request
        headers.update(self.headers)

        path = self.path_get_entity_attrs.replace('entityId', entity_id)

        return self.__send_request('get', path, headers=headers, verify=None, query=params)

    def get_attribute(self, headers, entity_id, entity_type, attribute_name):
        """
        GET
        http://orion.lab.fiware.org/v2/entities/entityId/attrs/attrName?type=type

        Parameters
        entityId:
            Entity ID Example: Bcn_Welt. (String)
        type:
            Entity type, to avoid ambiguity in the case there are several entities with the same entity id. (String)
        attrName:
            Attribute to be retrieved. Example: temperature. (String)

        Response
        200
        HEADERS
            Content-Type:application/json
        BODY
        {
            "value": 21.7,
            "type": "none",
            "metadata": {}
        }

        :param entity_id:
        :param entity_type:
        :param attribute_name:
        :return:
        """

        # Add default headers to the request
        headers.update(self.headers)

        # Compose path
        path = self.path_entities_id_attrs_attr.replace('entityId', entity_id).replace('attrName', attribute_name)

        # Compose params
        params = {'type': entity_type}

        # Make request
        return self.__send_request('get', path, headers=headers, verify=None, query=params)

    def delete_entity(self, entity_id, entity_type=None):
        """
        DELETE /v2/entities/{entity_id}?type={entity_type}

        Parameters
        entity_id:
            Entity ID Example: Bcn_Welt. (String)
        entity_type (optional):
            Entity type, to avoid ambiguity in the case there are several entities with the same entity id. (String)

        Response
        204

        :param entity_id:
        :param entity_type:
        :return:
        """

        # Compose path
        path = self.path_delete_entity.replace('entityId', entity_id)

        # Compose params
        params = {}
        if entity_type is not None:
            params['type'] = entity_type

        # Make request
        return self.__send_request('delete', path, headers=self.headers, verify=None, query=params)

    def retrieve_subscriptions(self, headers={}, options=None):
        """
        Response
        200
        BODY
        [
            {
                "id": "abcdefg",
                "description": "One subscription to rule them all",
                "subject": {
                    "entities": [
                        {
                            "id": "Bcn_Welt",
                            "type": "Room"
                        }
                    ],
                    "condition": {
                        "attrs": [
                            "temperature "
                        ],
                        "expression": {
                            "q": "temperature>40"
                        }
                    }
                },
                "notification": {
                    "httpCustom": {
                        "url": "http://localhost:1234",
                        "headers": {
                            "X-MyHeader": "foo"
                        },
                        "qs": {
                            "authToken": "bar"
                        }
                    },
                    "attrsFormat": "keyValues",
                    "attrs": [
                        "temperature",
                        "humidity"
                    ],
                    "timesSent": 12,
                    "lastNotification": "2015-10-05T16:00:00.00Z"
                },
                "expires": "2016-04-05T14:00:00.00Z",
                "status": "active",
                "throttling": 5
            }
        ]
        """

        # Add default headers to the request
        headers.update(self.headers)

        # Check params is a correct dict
        if options is not None:
            if not isinstance(options, dict):
                raise Exception('Wrong type in options. Dictionary is needed')

        # Make request
        return self.__send_request('get', self.path_subscriptions, headers=headers, verify=None, query=options)

    def retrieve_subscription_by_id(self, headers, subscription_id):
        """
        Response
        200
        HEADERS
            Content-Type:application/json
        BODY
        {
            "id": "abcdef",
            "description": "One subscription to rule them all",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Room"
                    }
                ],
                "condition": {
                    "attrs": [ "temperature " ],
                    "expression": {
                        "q": "temperature>40"
                    }
                }
            },
            "notification": {
                "http": {
                    "url": "http://localhost:1234"
                },
                "attrs": ["temperature", "humidity"],
                "timesSent": 12,
                "lastNotification": "2015-10-05T16:00:00.00Z"
            },
            "expires": "2016-04-05T14:00:00.00Z",
            "status": "active",
            "throttling": 5,
        }
        :param headers:
        :param options:
        :return:
        """

        # Add default headers to the request
        headers.update(self.headers)

        # Compose path
        path = self.path_subscriptions_by_id.replace('subscriptionId', subscription_id)

        # Make request
        return self.__send_request('get', path, headers=headers, verify=None)

    def create_subscription(self, payload, headers={}):
        """
        Response
        201

        BODY
        {
            "id": "abcdef",
            "description": "One subscription to rule them all",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Room"
                    }
                ],
                "condition": {
                    "attrs": [ "temperature " ],
                    "expression": {
                        "q": "temperature>40"
                    }
                }
            },
            "notification": {
                "http": {
                    "url": "http://localhost:1234"
                },
                "attrs": ["temperature", "humidity"],
            },
            "expires": "2016-04-05T14:00:00.00Z",
            "throttling": 5,
        }
        :param headers:
        :return:
        """

        # Add default headers to the request
        headers.update(self.headers)

        # Compose path
        path = self.path_subscriptions

        # Make request
        return self.__send_request('post', path, payload=payload, headers=headers, verify=None)

    def delete_subscription(self, sub_id):
        """
        DELETE /v2/subscriptions/{sub_id}

        Parameters
        sub_id:

        Response
        204

        :param sub_id:
        :return:
        """

        # Compose path
        path = self.path_subscriptions_by_id.replace('subscriptionId', sub_id)

        # Make request
        return self.__send_request('delete', path, headers=self.headers, verify=None)


if __name__ == '__main__':
    # Example if use of the library as a client
    cb = CbNgsi10v2Utils('127.0.0.1', 'http')

    # ====================create entity================
    # Compose the metadatas
    md = MetadataV2(md_name='crs', md_value='WGS84')
    md2 = MetadataV2(md_name='crs2', md_value='WGS83')
    print(md.get_metadata())

    # Compose the attributes
    attr = AttributeV2(att_name='location', att_value='41.3763726, 2.1864475', att_type='geo:point')
    attr.add_metadata(md)
    attr.add_metadata(md2)
    attr2 = AttributeV2(att_name='temperature', att_value=21.7)
    attr3 = AttributeV2(att_name='humidity', att_value=120)
    print(attr.get_attribute())

    # Compose the entity
    ent1 = EntityV2(entity_id='Bcn-Welt25', entity_type='Room5')
    ent1.add_attribute(attr)
    ent1.add_attribute(attr2)
    ent1.add_attribute(attr3)
    print(ent1.get_entity())

    # create payload
    pl = PayloadUtilsV2.build_create_entity_payload(ent1)

    # invoke CB
    headers = {'fiware-service': 'city012', 'fiware-servicepath': '/electricidad'}
    # headers = {'fiware-service': 'eeee', 'fiware-servicepath': '/uuu'}
    resp = cb.create_entity(headers=headers, payload=pl)

    # ====================list entities================
    # create filters
    filters2 = {'type': 'Room5', 'limit': 3, 'q': 'humidity~=120;temperature~=21.7'}
    filters = {'q': 'dateCreated>2016-04-04T14:00:00.00Z', 'options':'dateCreated'}
    # invoke CB
    resp = cb.list_entities(headers=headers, filters=filters2)

    # ===================get attribute data============

    # Get attribute data
    # resp = cb.get_attribute(headers=headers, entity_id='Bcn-Welt25', entity_type='Room5', attribute_name='location')


    # ===============retrieve subscriptions============

    parameteres = {'limit': 1, 'offset': 4, 'options': 'count'}
    wrong_parameters = '23'
    # resp = cb.retrieve_subscriptions(headers=headers, options=parameteres)
    # resp = cb.retrieve_subscriptions(headers=headers, options=wrong_parameters)

    # ===============retrieve subscriptions by id ============

    id = '572b35cc377ea57e2ay69771'
    # resp = cb.retrieve_subscription_by_id(headers=headers, subscription_id=id)
