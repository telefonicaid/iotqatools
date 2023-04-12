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

__author__ = 'Jon & xvc'

import pystache
import requests
import json

import  copy
from iotqatools.templates.cb_templates import *
from iotqatools.iot_logger import get_logger
from requests.exceptions import RequestException
from iotqatools.iot_tools import PqaTools


# Utilities
def check_valid_json(payload):
    """
    Checks if the argument is a JSON transformation valid, and return it in JSON
    :param json:
    :return:
    """
    if type(payload) is str or type(payload) is unicode:
        try:
            return json.loads(str(payload).replace('\'', '"'))
        except Exception as e:
            raise ValueError('JSON parse error in your string, check it: {string}'.format(string=payload))
    elif type(payload) is dict:
        return payload
    else:
        raise ValueError('The payloads can be only a string or a dict')


def pretty_json(json_to_print):
    """
    Fucntion that return a json with tabs to a pretty print
    :param json_to_print:
    :return:
    """
    return json.dumps(json_to_print, sort_keys=True, indent=4, separators=(',', ': '))


def check_minimal_attrs_payload(atrs_list, payload, log):
    """
    Check if the payload dict has the minimal attrs needed
    :param atrs_list:
    :param payload:
    :param log:
    :return:
    """
    if type(atrs_list) is not list:
        raise ValueError("The attributes to check has to be a list, but is: {attrs_list_type}".format(
            attrs_list_type=str(type(atrs_list))))
    if type(payload) is not dict:
        raise ValueError(
            "The payload has to be a python dict, but is: {payload_type}".format(payload_type=str(type(payload))))
    for attr in atrs_list:
        if attr not in payload:
            log.warn(
                "The payload to sent to CB has not \"{attr}\" attribute. \n Check the payload: \n {payload}".format(
                    attr=attr, payload=pretty_json(payload)))


class EntitiesConsults(object):
    """
    Class that represent the entities to build the payload to send to a contextBroker.
    The format created is:
    [
        {
            "type": "Room",
            "isPattern": "false",
            "id": "Room1"
        },
        {
            "type": "Room",
            "isPattern": "false",
            "id": "Room2"
        }
    ]
    """

    def __init__(self):
        self.entities_list = []

    def add_entity(self, entity_id, entity_type, is_pattern="false"):
        self.entities_list.append({'type': entity_type, 'isPattern': is_pattern, 'id': entity_id})

    def get_entities(self):
        return self.entities_list


class AttributesConsults(object):
    """
    Class that represent the attributes to build the payload to send to a contextBroker
    The format created is:
    [
        {
            "name": "temperature",
            "type": "float",
            "isDomain": "false"
        },
        {
            "name": "pressure",
            "type": "integer",
            "isDomain": "false"
        }
    ]
    """

    def __init__(self):
        self.attributes_list = []

    def add_attribute(self, attribute_name, attribute_type, is_domain="false"):
        self.attributes_list.append({'name': attribute_name, 'type': attribute_type, 'isDomain': is_domain})

    def get_attributes(self):
        return self.attributes_list


class MetadatasCreation(object):
    """
    Class that represent the metadata to build the attribute
    The format created is:
    [
            {
                "name": "temperature",
                "type": "float",
                "value": "23"
            },
            {
                "name": "pressure",
                "type": "integer",
                "value": "720"
            }
    ]
    """

    def __init__(self):
        self.metadatas_list = []

    def add_metadata(self, metadata_name, metadata_type, value):
        self.metadatas_list.append({'name': metadata_name, 'type': metadata_type, 'value': value})

    def get_metadatas(self):
        return self.metadatas_list


class AttributesCreation(object):
    """
    Class that represent the attributes to build the payload to send to a contextBroker
    The format created is:
    [
            {
                "name": "temperature",
                "type": "float",
                "value": "23"
            },
            {
                "name": "pressure",
                "type": "integer",
                "value": "720"
            }
    ]
    """

    def __init__(self):
        self.attributes_list = []

    def add_attribute(self, attribute_name, attribute_type, value, metadatas=None):
        if metadatas is not None:
            if not isinstance(metadatas, MetadatasCreation):
                raise ValueError('The metadatas argument has to be an instance of MetadatasCreation class')
            self.attributes_list.append({'name': attribute_name, 'type': attribute_type, 'value': value,
                                         'metadatas': metadatas.get_metadatas()})
        else:
            self.attributes_list.append({'name': attribute_name, 'type': attribute_type, 'value': value})

    def get_attributes(self):
        return self.attributes_list


class ContextElements(object):
    """
    Class that represent the attributes to build the payload to send to a contextBroker
    The format created is:
    [
        {
            "type": "Room",
            "isPattern": "false",
            "id": "Room1",
            "attributes": [
            {
                "name": "temperature",
                "type": "float",
                "value": "23"
            },
            {
                "name": "pressure",
                "type": "integer",
                "value": "720"
            }
            ]
        }
    ]
    """

    def __init__(self):
        self.context_elements_list = []

    def add_context_element(self, entity_id, entity_type, attributes, is_pattern="false"):
        if not isinstance(attributes, AttributesCreation):
            raise ValueError('The attributes argument has to be an instance of AttributesCreation class')
        self.context_elements_list.append(
            {'type': entity_type, 'isPattern': is_pattern, 'id': entity_id, 'attributes': attributes.get_attributes()})

    def get_context_elements(self):
        return self.context_elements_list


class NotifyConditions(object):
    """
    Class that represent the notify conditions to the subscriptions in ContextBroker
    The format is for ontime:
     [
        {
            "type": "ONTIMEINTERVAL",
            "condValues": [
                "PT10S"
            ]
        }
    ]
    The format is for onchange:
     [
        {
            "type": "ONCHANGE",
            "condValues": [
                "pressure", "temparature"
            ]
        }
    ]
    """

    def __init__(self):
        self.notify_conditions = []

    def add_notify_condition_ontime(self, time):
        self.notify_conditions.append({"type": "ONTIMEINTERVAL", "condValues": [time]})

    def add_notify_condition_onchange(self, attributes):
        if type(attributes) is not list:
            raise ValueError('The attributes argument has to be a list of strings with attributes')
        self.notify_conditions.append({"type": "ONCHANGE", "condValues": attributes})

    def get_notify_conditions(self):
        return self.notify_conditions


class ContextRegistrations(object):
    """
    Class that represents the registration to the Contexts Providers in the Context Broker
    The format is:
    [
        {
            "entities": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1"
                },
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room2"
                }
            ],
            "attributes": [
                {
                    "name": "temperature",
                    "type": "float",
                    "isDomain": "false"
                },
                {
                    "name": "pressure",
                    "type": "integer",
                    "isDomain": "false"
                }
            ],
            "providingApplication": "http://mysensors.com/Rooms"
        }
    ]
    """

    def __init__(self):
        self.context_registrations = []

    def add_context_registration(self, entities, attributes, providing_application):
        if not isinstance(entities, EntitiesConsults):
            raise ValueError('The "entities" argument has to be an instance of EntitiesConsults')
        if not isinstance(attributes, AttributesConsults):
            raise ValueError('The "attributes" argument has to be an instance of AttributesConsults')
        self.context_registrations.append(
            {"entities": entities.get_entities(), "attributes": attributes.get_attributes(),
             "providingApplication": providing_application})

    def get_context_registrations(self):
        return self.context_registrations


class PayloadUtils(object):
    """
    Class who construct the payloads
    """
    # TODO: geographical scopes
    # TODO: Pagination

    @staticmethod
    def build_standard_entity_creation_payload(context_elements):
        """
        Build the payload to send to context broker to create a new entity with the standard api
        The format is:
        {
            "contextElements": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1",
                    "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "value": "23"
                    },
                    {
                        "name": "pressure",
                        "type": "integer",
                        "value": "720"
                    }
                    ]
                }
            ],
            "updateAction": "APPEND"
        }
        :return:
        """
        if not isinstance(context_elements, ContextElements):
            raise ValueError('The context_elements argument has to be an instance of ContestElements')
        payload = {
            "contextElements": context_elements.get_context_elements(),
            "updateAction": "APPEND"
        }
        return payload

    @staticmethod
    def build_convenience_entity_creation_payload(attributes, entity_id=None, entity_type=""):
        """
        Build the payload to sed to context broker so create a new entity with the convenience api
        :param entity_id:
        :param attributes:
        :param entity_type:
        :return:
        There are two kind of payloads possibles
        Only atrributes:
        {
          "attributes" : [
            {
              "name" : "temperature",
              "type" : "float",
              "value" : "23"
            },
            {
              "name" : "pressure",
              "type" : "integer",
              "value" : "720"
            }
          ]
        }
        ------
        Attributes and entity with type
        {
          "id": "Room1",
          "type": "Room",
          "attributes" : [
            {
              "name" : "temperature",
              "type" : "float",
              "value" : "23"
            },
            {
              "name" : "pressure",
              "type" : "integer",
              "value" : "720"
            }
          ]
        }
        """
        if not isinstance(attributes, AttributesCreation):
            raise ValueError('The context_elements argument has to be an instance of ContestElements')
        payload = {'attributes': attributes.get_attributes()}
        if entity_id != None:
            payload.update({"id": entity_id})
            payload.update({"type": entity_type})
        return payload

    @staticmethod
    def build_standard_query_context_payload(entities, attributes=None):
        """
        Build the payload to send to consult for some entitys to cb
        :param entities:
        :param attributes:
        :return:
        The attributes is optional.
        The format is:
        {
          "entities": [
            {
                "type": "Room",
                "isPattern": "false",
                "id": "Room1"
            }
            ],
            "attributes" : [
                "temperature"
            ]
        }
        """
        if not isinstance(entities, EntitiesConsults):
            raise ValueError('The entities argument has to be an instance of EntitiesConsults')
        if attributes != None:
            if type(attributes) is not list:
                raise ValueError('The attributes argument has to be a list of strings')
        payload = {"entities": entities.get_entities()}
        if attributes is not None:
            payload.update({"attributes": attributes})
        return payload

    @staticmethod
    def build_standard_entity_update_payload(context_elements):
        """
        Build the payload to send to context broker to create a new entity with the standard api
        The format is:
        {
            "contextElements": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1",
                    "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "value": "23"
                    },
                    {
                        "name": "pressure",
                        "type": "integer",
                        "value": "720"
                    }
                    ]
                }
            ],
            "updateAction": "UPDATE"
        }
        :return:
        """
        if not isinstance(context_elements, ContextElements):
            raise ValueError('The context_elements argument has to be an instance of ContestElements')
        payload = {
            "contextElements": context_elements.get_context_elements(),
            "updateAction": "UPDATE"
        }
        return payload

    @staticmethod
    def build_standard_entity_delete_payload(context_elements):
        """
        Build the payload to send to context broker to create a new entity with the standard api
        The format is:
        {
            "contextElements": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1",
                    "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "value": "23"
                    },
                    {
                        "name": "pressure",
                        "type": "integer",
                        "value": "720"
                    }
                    ]
                }
            ],
            "updateAction": "DELETE"
        }
        :return:
        """
        if not isinstance(context_elements, ContextElements):
            raise ValueError('The context_elements argument has to be an instance of ContestElements')
        payload = {
            "contextElements": context_elements.get_context_elements(),
            "updateAction": "DELETE"
        }
        return payload

    @staticmethod
    def build_convenience_entity_update_payload(attributes, entity_id=None, entity_type=""):
        """
        Is the same payload as in the Creation
        :param attributes:
        :param entity_id:
        :param entity_type:
        :return:
        """
        return PayloadUtils.build_convenience_entity_creation_payload(attributes, entity_id, entity_type)

    @staticmethod
    def build_convenience_entity_delete_payload(attributes, entity_id=None, entity_type=""):
        """
        Is the same payload as in the Creation
        :param attributes:
        :param entity_id:
        :param entity_type:
        :return:
        """
        return PayloadUtils.build_convenience_entity_creation_payload(attributes, entity_id, entity_type)

    @staticmethod
    def build_standard_subscribe_context_payload(entities, attributes, reference, duration, notify_conditions,
                                                 throttling=None):
        """
        Build the payload to send to subscribe to an entity and his attributes
        :return:
        {
            "subject": {
                "entities": [
                    {
                    "idPattern": ".*",
                    "type": "Room"
                    }
                ],
                "condition": {
                    "attrs": [ "temperature" ]
                }
            },
            "notification": {
                "http": {
                    "url": "http://localhost:1234"
                },
                "attrs": ["temperature", "humidity"]
            },
            "expires": "2025-04-05T14:00:00.00Z",
            "throttling": 5
        }

        """
        if not isinstance(entities, EntitiesConsults):
            raise ValueError('The entities argument has to be an instance of EntitiesConsults')
        if type(attributes) is not list:
            raise ValueError('The attributes argument has to be a list of strings')
        if not isinstance(notify_conditions, NotifyConditions):
            raise ValueError('The notify_conditions has to be an instance of NotifyConditions')

        # FIXME: entities.get_entities() returns the entities in NGSIv1 format, so we need to adapt.
        # entities parameter shouldn't be in NGSIv1 (build_standard_subscribe_context_payload callers should be adapted)
        entities_v2 = []
        for entity in entities.get_entities():
            entity_v2 = {
                'type': entity['type']
            }
            if entity['isPattern'] == 'false':
                entity_v2['id'] = entity['id']
            else:
                entity_v2['idPattern'] = entity['id']
            entities_v2.append(entity_v2)

        # FIXME: notify_conditions.get_notify_conditions() return NGSIv1 conditions payloads, so we need to adapt
        # this shouldn't be used (build_standard_subscribe_context_payload callers should be adapted)
        condition_attributes = []
        for nc in notify_conditions.get_notify_conditions():
            if nc['type'] == 'ONCHANGE':  # ONTIMEINTERVAL shouldn't be in use in test, anyway...
                condition_attributes.extend(nc['condValues'])

        subject = {
            'entities': entities_v2,
            'condition': {
                'attrs': condition_attributes
            }
        }

        notification = {
            'http': {
                'url': reference
            },
            'attrs': attributes
        }

        payload = {
            'subject': subject,
            'notification0': notification
        }

        # duration should be used to set expires based on current time + duration. However, we don't have
        # any .feature checking duration expiration, so we can omit the field for permanent subscriptions
        # FIXME: duration should be removed from function signature

        # throttling should be moved from Pxx format to plain seconds. However, it is always set to None in
        # existing .feature, so we can omit the field
        # FIXME: throttling should be removed from function signature

        return payload

    @staticmethod
    def build_standard_unsubscribe_context_payload(subscription_id):
        """
        Build the payload to send to unsubscribe from context Broker
        :param subscription_id:
        :return:
        The format is:
        {
          "subscriptionId": "51c04a21d714fb3b37d7d5a7"
        }
        """
        payload = {"subscriptionId": subscription_id}
        return payload

    # NGSI 9 -----------------------------------------------------------------------------------------------

    @staticmethod
    def build_context_registration_payload(context_registrations, duration):
        """
        Build the payload to send to register a context provider.
        Entities and attributes has to be list of entities or attributes
        The format is:
        {
            "contextRegistrations": [
                {
                    "entities": [
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room1"
                        },
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room2"
                        }
                    ],
                    "attributes": [
                        {
                            "name": "temperature",
                            "type": "float",
                            "isDomain": "false"
                        },
                        {
                            "name": "pressure",
                            "type": "integer",
                            "isDomain": "false"
                        }
                    ],
                    "providingApplication": "http://mysensors.com/Rooms"
                }
            ],
            "duration": "P1M"
        }
        """
        if not isinstance(context_registrations, ContextRegistrations):
            raise ValueError('The context_registrations argument has to be a instance of ContextRegistrations')
        payload = {
            'contextRegistrations': context_registrations.get_context_registrations(),
            'duration': duration
        }
        return payload

    @staticmethod
    def build_context_update_payload(context_registrations, duration, registration_id):
        """
        Build the payload to send to update a registration of a context provider.
        Entities and attributes has to be list of entities or attributes, ant the registration_id is needed
        The format is:
        {
            "contextRegistrations": [
                {
                    "entities": [
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room1"
                        },
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room2"
                        }
                    ],
                    "attributes": [
                        {
                            "name": "temperature",
                            "type": "float",
                            "isDomain": "false"
                        },
                        {
                            "name": "pressure",
                            "type": "integer",
                            "isDomain": "false"
                        }
                    ],
                    "providingApplication": "http://mysensors.com/Rooms"
                }
            ],
            "duration": "P1M",
            "registrationId": "aaaa"
        }
        """
        if not isinstance(context_registrations, ContextRegistrations):
            raise ValueError('The context_registrations argument has to be a instance of ContextRegistrations')
        payload = {
            'contextRegistrations': context_registrations.get_context_registrations(),
            'duration': duration,
            'registrationId': registration_id
        }

        return payload

    @staticmethod
    def build_subscribe_context_availability_payload(entities, attributes, reference, duration):
        """
        Build the subscribe context availability payload
        The format is:
        {
            "entities": [
            {
                "type": "Room",
                "isPattern": "true",
                "id": ".*"
            }
            ],
            "attributes": [
            "temperature"
            ],
            "reference": "http://localhost:1028/accumulate",
            "duration": "P1M"
        }
        """
        if not isinstance(entities, EntitiesConsults):
            raise ValueError('The entities argument has to be an instance of EntitiesConsults')
        if type(attributes) is not list:
            raise ValueError('The attributes argument has to be a list of strings')
        payload = {
            "entities": entities.get_entities(),
            "attributes": attributes,
            "reference": reference,
            "duration": duration
        }
        return payload

    @staticmethod
    def build_update_context_availability_subscription_payload(entities, subscription_id, attributes=None,
                                                               duration=None):
        """
        Build the update context availability subscription
        The format is
        {
            "entities": [
            {
                "type": "Car",
                "isPattern": "true",
                "id": ".*"
            }
            ],
            "attributes": ["temperature"]
            "duration": "P1M",
            "subscriptionId": "52a745e011f5816465943d59"
        }
        """
        if not isinstance(entities, EntitiesConsults):
            raise ValueError('The entities argument has to be an instance of EntitiesConsults')
        if attributes != None:
            if type(attributes) is not list:
                raise ValueError('The attributes argument has to be a list of strings')
        payload = {
            "entities": entities.get_entities(),
            "subscriptionId": subscription_id
        }
        if attributes is not None:
            payload.update({"attributes": attributes})
        if duration is not None:
            payload.update({"duration": duration})
        return payload

    @staticmethod
    def build_unsubscribe_context_availability_payload(subscription_id):
        """
        Build the unsubscribe context availability subscription
        The format is:
        {
            "subscriptionId": "52a745e011f5816465943d59"
        }
        """
        payload = {"subscriptionId": subscription_id}
        return payload

    @staticmethod
    def build_discover_context_availability_payload(entities):
        """
        Build the unsubscribe context availability subscription
        The format is:
        {
            "entities": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1"
                }
            ]
        }
        """
        payload = {'entities': entities.get_entities()}
        return payload

    @staticmethod
    def build_convenience_register_context_payload(duration, providing_application):
        """
        Build the CONVENIENCE register context payload
        The format is_
        {
          "duration" : "P1M",
          "providingApplication" : "http://mysensors.com/Rooms"
        }
        """
        payload = {'duration': duration, 'providingApplication': providing_application}
        return payload


class CbNgsi10Utils(object):
    """
    Basic functionality for ContextBroker
    """

    def __init__(self, instance, service=None, subservice=None,
                 protocol="http",
                 port="1026",
                 path_context_entities="/v1/contextEntities",
                 path_context_entity_types="/v1/contextEntityTypes",
                 path_query_context="/v1/queryContext",
                 path_statistics="/statistics",
                 path_subscribe_context="/v2/subscriptions",
                 path_update_context="/v1/updateContext",
                 path_update_context_subscription="/v1/updateContextSubscription",
                 path_unsubscribe_context="/v1/unsubscribeContext",
                 path_context_subscriptions="/v2/subscriptions",   # FIXME: in NGSIv2 we only have a URL for this. Unify
                 path_version="/version",
                 log_instance=None,
                 log_verbosity='DEBUG',
                 default_headers={"Accept": "application/json", 'content-type': 'application/json'},
                 check_json=True,
                 verify=False):
        """
        CB Utils constructor
        :param instance:
        :param service:
        :param subservice:
        :param protocol:
        :param port:
        :param path_context_entities:
        :param path_context_entity_types:
        :param path_query_context:
        :param path_statistics:
        :param path_subscribe_context:
        :param path_update_context:
        :param path_update_context_subscription:
        :param path_unsubscribe_context:
        :param path_context_subscriptions:
        :param path_version:
        :param log_instance:
        :param log_verbosity:
        :param default_headers:
        :param check_json:
        :param verify: ssl check
        """
        # initialize logger
        if log_instance is not None:
            self.log = log_instance
        else:
            self.log = get_logger('CbNgsi10Utils', log_verbosity)

        # Assign the values
        self.default_endpoint = protocol + '://' + instance + ':' + port
        self.headers = self.__set_headers(default_headers, service, subservice)
        self.path_context_entities = self.default_endpoint + path_context_entities
        self.path_context_entity_types = self.default_endpoint + path_context_entity_types
        self.path_query_context = self.default_endpoint + path_query_context
        self.path_statistics = path_statistics
        self.path_subscribe_context = self.default_endpoint + path_subscribe_context
        self.path_update_context = self.default_endpoint + path_update_context
        self.path_update_context_subscription = self.default_endpoint + path_update_context_subscription
        self.path_unsubscribe_context = self.default_endpoint + path_unsubscribe_context
        self.path_context_subscriptions = self.default_endpoint + path_context_subscriptions
        self.path_version = path_version
        self.check_json = check_json
        self.verify = verify

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
            parameters.update({'verify': self.verify})

        # Remove the content-type header if it is a GET or DELETE method
        if method.lower() in ("get", "delete"):
            if "content-type" in parameters["headers"]:
                parameters["headers"].pop("content-type", None)
            elif "Content-Type" in parameters["headers"]:  # used in Requests library version 2.11.1 or higher
                parameters["headers"].pop("Content-Type", None)

        # Send the requests
        try:
            response = requests.request(**parameters)
        except RequestException, e:
            PqaTools.log_requestAndResponse(url=url, headers=headers, data=payload, comp='CB', method=method)
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)

        # Log data
        PqaTools.log_fullRequest(comp='CB', response=response, params=parameters)

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
        if subservice != "None" and subservice != "none" and subservice != None:
            self.headers['Fiware-Servicepath'] = subservice

    def set_auth_token(self, auth_token):
        self.headers['x-auth-token'] = auth_token

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

    def standard_entity_creation(self, payload):
        """
        Create a entity in ContextBroker with the standard entity creation
        :param payload:
        :param service:
        :param subservice:
        :return:
        The payload has to be like:
        {
            "contextElements": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1",
                    "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "value": "23"
                    },
                    {
                        "name": "pressure",
                        "type": "integer",
                        "value": "720"
                    }
                    ]
                }
            ],
            "updateAction": "APPEND"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            # Checks the payload to send
            check_minimal_attrs_payload(["contextElements", "updateAction"], payload, self.log)
            if "updateAction" in payload:
                if payload['updateAction'] != "APPEND":
                    self.log.warn("The action of the creation is not \"APPEND\"")
        return self.__send_request('post', self.path_update_context, self.headers, payload)

    def convenience_entity_creation_url_method(self, entity_id, payload, entity_type=None, verify=None):
        """
        Create an entity in Context Broker with the convenience entity creation.
        There are two ways to create:
            - Specify the Id in the url with no Type (.../contextEntity/<entity_id>)
            - Specify the Id and the Type in te url (.../contextEntity/type/<type>/id/<id>
        :param entity_id:
        :param payload:
        :param service:
        :param subservice:
        :param entity_type:
        :return:
        Payload
        {
          "attributes" : [
            {
              "name" : "temperature",
              "type" : "float",
              "value" : "21"
            },
            {
              "name" : "pressure",
              "type" : "integer",
              "value" : "711"
            }
          ]
        }
        """

        if entity_type is None:
            url = self.path_context_entities + '/{entity_id}'.format(entity_id=entity_id)
        else:
            url = self.path_context_entities + '/type/{entity_type}/id/{entity_id}'.format(entity_type=entity_type,
                                                                                           entity_id=entity_id)
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["attributes"], payload, self.log)
        return self.__send_request('post', url, self.headers, payload, verify=verify)

    def convenience_entity_creation_payload_method(self, payload, verify=None):
        """
        Create an entity in Context Broker with the convenience entity creation.
        The entity and his type is indicated in the payload
        :param payload:
        :param service:
        :param subservice:
        :return:
        Payload with entity information
        {
          "id": "Room1",
          "type": "Room",
          "attributes" : [
            {
              "name" : "temperature",
              "type" : "float",
              "value" : "23"
            },
            {
              "name" : "pressure",
              "type" : "integer",
              "value" : "720"
            }
          ]
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["attributes", "id", "type"], payload, self.log)
        return self.__send_request('post', self.path_context_entities, self.headers, payload, verify=verify)

    def standard_query_context(self, payload):
        """
        Query an entity with the possibility of filtering for the attributes
        :param payload:
        :param service:
        :param subservice:
        :return:
        payload:
        {
            "entities": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1"
                }
            ],
            "attributes" : [
                "temperature"
            ]
        }
        """


        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["entities"], payload, self.log)
        return self.__send_request('post', self.path_query_context, self.headers, payload)

    def convenience_query_context(self, entity_id=None, entity_type=None, attribute=None, verify=None):
        """
        Query an entity with the possibility of filtering for the attribute, and the posiibility
        of not send entity retrieving all entities
        :
        :param entity_id:
        :param entity_type:
        :param attribute:
        :return:
        """
        self.remove_content_type_header()
        if entity_id is not None:
            url = self.path_context_entities
            if entity_type is not None:
                url += u'/type/{entity_type}/id/{entity_id}'.format(entity_type=entity_type, entity_id=entity_id)
            else:
                url += u'/{entity_id}'.format(entity_type=entity_type, entity_id=entity_id)
            if attribute is not None:
                url += u'/attributes/{attribute}'.format(attribute=attribute)
        else:
            if entity_type is not None:
                url = self.path_context_entity_types
                if attribute is not None:
                    url += '/{entity_type}/attributes/{attribute}'.format(entity_type=entity_type, attribute=attribute)
                else:
                    url += '/{entity_type}'.format(entity_type=entity_type)
            else:
                # Retrieve all entities with all attributes
                url = self.path_context_entities

        return self.__send_request('get', url, self.headers, verify=verify)

    def standard_entity_update(self, payload):
        """
        Create a entity in ContextBroker with the standard entity creation
        :param payload:
        :param service:
        :param subservice:
        :return:
        The payload has to be like:
        {
            "contextElements": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1",
                    "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "value": "23"
                    },
                    {
                        "name": "pressure",
                        "type": "integer",
                        "value": "720"
                    }
                    ]
                }
            ],
            "updateAction": "UPDATE"
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["contextElements", "updateAction"], payload, self.log)
            if "updateAction" in payload:
                if payload['updateAction'] != "UPDATE":
                    self.log.warn("The action of the creation is not \"UPDATE\", is: {updateaction}".format(
                        updateaction=payload['updateSction']))
        return self.__send_request('post', self.path_update_context, self.headers, payload)

    def convenience_entity_update_url_method(self, entity_id, payload, entity_type=None):
        """
        Update an entity in Context Broker with the convenience entity udpate.
        There are two ways to create:
            - Specify the Id in the url with no Type (.../contextEntity/<entity_id>)
            - Specify the Id and the Type in te url (.../contextEntity/type/<type>/id/<id>
        :param entity_id:
        :param payload:
        :param service:
        :param subservice:
        :param entity_type:
        :return:
        Payload
        {
          "attributes" : [
            {
              "name" : "temperature",
              "type" : "float",
              "value" : "21"
            },
            {
              "name" : "pressure",
              "type" : "integer",
              "value" : "711"
            }
          ]
        }
        """

        if entity_type is None:
            url = self.path_context_entities + '/{entity_id}'.format(entity_id=entity_id)
        else:
            url = self.path_context_entities + '/type/{entity_type}/id/{entity_id}'.format(entity_type=entity_type,
                                                                                           entity_id=entity_id)
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["attributes"], payload, self.log)
        self.headers['content-type'] = "application/json"
        return self.__send_request('put', url, self.headers, payload)

    def convenience_entity_update_payload_method(self, payload):
        """
        Update an entity in Context Broker with the convenience entity update.
        The entity and his type is indicated in the payload
        :param payload:
        :return:
        Payload with entity information
        {
          "id": "Room1",
          "type": "Room",
          "attributes" : [
            {
              "name" : "temperature",
              "type" : "float",
              "value" : "23"
            },
            {
              "name" : "pressure",
              "type" : "integer",
              "value" : "720"
            }
          ]
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["attributes", "id", "type"], payload, self.log)
        return self.__send_request('put', self.path_context_entities, self.headers, payload)

    # **
    def standard_entity_delete(self, payload):
        """
        Delete a entity in ContextBroker with the standard entity deletion
        :param payload:
        :return:
        The payload has to be like:
        {
            "contextElements": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1",
                    "attributes": [
                    {
                        "name": "temperature",
                        "type": "float",
                        "value": "23"
                    },
                    {
                        "name": "pressure",
                        "type": "integer",
                        "value": "720"
                    }
                    ]
                }
            ],
            "updateAction": "DELETE"
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["contextElements", "updateAction"], payload, self.log)
            if "updateAction" in payload:
                if payload['updateAction'] != "DELETE":
                    self.log.warn("The action of the creation is not \"DELETE\", is: {updateaction}".format(
                        updateaction=payload['updateSction']))
        return self.__send_request('post', self.path_update_context, self.headers, payload)

    def convenience_entity_delete_url_method(self, entity_id, entity_type=None, service='', service_path=''):
        """
        Delete an entity in Context Broker with the convenience entity deletion.
        There are two ways to create:
            - Specify the Id in the url with no Type (.../contextEntity/<entity_id>)
            - Specify the Id and the Type in te url (.../contextEntity/type/<type>/id/<id>
        :param entity_id:
        :param entity_type:
        :return:
        """

        if entity_type is None:
            url = self.path_context_entities + '/{entity_id}'.format(entity_id=entity_id)
        else:
            url = self.path_context_entities + '/type/{entity_type}/id/{entity_id}'.format(entity_type=entity_type,
                                                                                           entity_id=entity_id)

        myheaders = copy.deepcopy(self.headers)
        if service:
            myheaders["Fiware-Service"]= service
        if service_path:
            myheaders["Fiware-ServicePath"]= service_path

        return self.__send_request('delete', url, myheaders)

    # **

    def standard_subscribe_context_onchange(self, payload):
        """
        Create a subscription in the context broker
        :param payload:
        The format of the payload is:
        {
            "entities": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1"
                }
            ],
            "attributes": [
                "temperature"
            ],
            "reference": "http://localhost:1028/accumulate",
            "duration": "P1M",
            "notifyConditions": [
                {
                    "type": "ONCHANGE",
                    "condValues": [
                        "pressure"
                    ]
                }
            ],
            "throttling": "PT5S"
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(
                ["entities", "attributes", "reference", "duration", "notifyConditions", "throttling"], payload,
                self.log)
        return self.__send_request('post', self.path_subscribe_context, self.headers, payload)

    def convenience_subscribe_context_onchange(self, payload):
        """
        Create a subscription in the context broker
        :param payload:
        The format of the payload is:
        {
            "entities": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1"
                }
            ],
            "attributes": [
                "temperature"
            ],
            "reference": "http://localhost:1028/accumulate",
            "duration": "P1M",
            "notifyConditions": [
                {
                    "type": "ONCHANGE",
                    "condValues": [
                        "pressure"
                    ]
                }
            ],
            "throttling": "PT5S"
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            # FIXME: no longer needed? Eventually remove this fragment
            #check_minimal_attrs_payload(
            #    ["entities", "attributes", "reference", "duration", "notifyConditions", "throttling"], payload,
            #    self.log)
        return self.__send_request('post', self.path_context_subscriptions, self.headers, payload)

    def standard_update_context_subscription(self, payload):
        """
        Update the context subscription in the context broker
        :param payload:
        :return:
        The payload format is:
        {
            "subscriptionId": "51c04a21d714fb3b37d7d5a7",
            "duration": "P1M",
            "notifyConditions": [
                {
                    "type": "ONTIMEINTERVAL",
                    "condValues": [
                        "PT10S"
                    ]
                }
            ],
            "throttling": ""
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["subscriptionId"], payload, self.log)
        return self.__send_request('post', self.path_update_context_subscription, self.headers, payload)

    def convenience_update_context_subscription(self, subscription_id, payload):
        """
        Update the context subscription in the context broker with the convenience method
        :param subscription_id:
        :param payload:
        :return:
        The payload format is:
        {
            "subscriptionId": "51c04a21d714fb3b37d7d5a7",
            "duration": "P1M",
            "notifyConditions": [
                {
                    "type": "ONTIMEINTERVAL",
                    "condValues": [
                        "PT10S"
                    ]
                }
            ],
            "throttling": ""
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["subscriptionId"], payload, self.log)
            if 'subscriptionId' in payload:
                if "subscriptionId" not in payload or subscription_id != payload['subscriptionId']:
                    self.log.warn("The subscription of the url an the subscription of the payload are different")
        return self.__send_request('put', self.path_context_subscriptions + '/{subscription_id}'.format(
            subscription_id=subscription_id), self.headers, payload)

    def standard_unsubscribe_context(self, payload):
        """
        Unsubscribe from a context broker
        :param payload:
        :return:
        The format of the payload is:
        {
          "subscriptionId": "51c04a21d714fb3b37d7d5a7"
        }
        """
        # Checks the payload to send
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["subscriptionId"], payload, self.log)
        return self.__send_request('post', self.path_unsubscribe_context, self.headers, payload)

    def convenience_unsubscribe_context(self, subscription_id):
        """
        Unsubscribe from a context broker with the convenience method
        :param subscription_id:
        :return:
        """
        return self.__send_request('delete', self.path_context_subscriptions + '/{subscription_id}'.format(
            subscription_id=subscription_id), self.headers)

    def get_attribute_values(self, entity_id=None, entity_type=None, attribute_name=None):
        """
        Returns the value of an attribute given  the entity and the attribute name
        :param entity_id: id of the entity
        :param attribute_name: name of the attribute
        :return: None if the attribute does noy exist or if the entity does not exists, otherwise it returns the value
        of the attribute
        """
        # Get the entity

        response = self.convenience_query_context(entity_id=entity_id, entity_type=entity_type,
                                                  attribute=attribute_name)
        assert response.status_code == 200, 'ERROR, entity cannot be retrieved'
        resp = None
        # Go through the response to find out the attribute value
        try:
            attributes_list = response.json()['attributes']
            for attribute in attributes_list:
                if attribute['name'] == attribute_name:
                    resp = attribute['value']
                    break
            return resp
        except KeyError:
            return resp


class CbNgsi9Utils():
    def __init__(self, instance, service, subservice='/',
                 protocol='http',
                 port='1026',
                 path_register_context='/v1/registry/registerContext',
                 path_discover_context_availability='/v1/registry/discoverContextAvailability',
                 path_subscribe_context_availability='/v1/registry/subscribeContextAvailability',
                 path_update_context_availability_subscription='/v1/registry/updateContextAvailabilitySubscription',
                 path_unsubscribe_context_availability='/v1/registry/unsubscribeContextAvailability',
                 path_verstion='/version',
                 path_convenience_operations='/v1/registry/contextEntities',
                 path_convenience_type_operations='/v1/registry/contextEntityTypes',
                 path_convenience_context_availability='/v1/registry/contextAvailabilitySubscriptions',
                 log_instance=None,
                 log_verbosity='INFO',
                 default_headers={"Accept": "application/json", 'content-type': 'application/json'},
                 check_json=True):
        """
        Library to do petitions to the ngsi9 api
        :param path_verstion:
        :param log_instance:
        :param log_verbosity:
        :param check_json:
        :param instance:
        :param protocol:
        :param port:
        :param path_register_context:
        :param path_discover_context_availability:
        :param path_subscribe_context_availability:
        :param path_update_context_availability_subscription:
        :param path_unsubscribe_context_availability:
        :param default_headers:
        :return:
        """
        if log_instance is not None:
            self.log = log_instance
        else:
            self.log = get_logger('CbNgsi9Utils', log_verbosity)
        self.default_endpoint = protocol + '://' + instance + ':' + port
        self.path_register_context = self.default_endpoint + path_register_context
        self.path_discover_context_availability = self.default_endpoint + path_discover_context_availability
        self.path_subscribe_context_availability = self.default_endpoint + path_subscribe_context_availability
        self.path_update_context_availability_subscription = self.default_endpoint + path_update_context_availability_subscription
        self.path_unsubscribe_context_availability = self.default_endpoint + path_unsubscribe_context_availability
        self.path_version = self.default_endpoint + path_verstion
        self.path_convenience = self.default_endpoint + path_convenience_operations
        self.path_convenience_types = self.default_endpoint + path_convenience_type_operations
        self.path_convenience_context_availability = self.default_endpoint + path_convenience_context_availability
        self.headers = self.__set_headers(default_headers, service, subservice)
        self.check_json = check_json

    def __send_request(self, method, url, headers=None, payload=None, verify=None, query=None):
        """
        Send a request to a specific url in a specifig type of http request
        :param method:
        :param url:
        :param headers:
        :param payload:
        :param verify:
        :param query:
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

        # Send the requests
        try:
            response = requests.request(**parameters)
        except RequestException, e:
            PqaTools.log_requestAndResponse(url=url, headers=headers, data=payload, comp='CB', method=method)
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)
        print response

        # Log data
        PqaTools.log_fullRequest(comp='CB', response=response, params=parameters)

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

    def register_context(self, payload):
        """
        :param payload:
        :param service:
        :param subservice:
        :return:
        Register a ContextProvider
        The format is:
        {
            "contextRegistrations": [
                {
                    "entities": [
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room1"
                        },
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room2"
                        }
                    ],
                    "attributes": [
                        {
                            "name": "temperature",
                            "type": "float",
                            "isDomain": "false"
                        },
                        {
                            "name": "pressure",
                            "type": "integer",
                            "isDomain": "false"
                        }
                    ],
                    "providingApplication": "http://mysensors.com/Rooms"
                }
            ],
            "duration": "P1M"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["contextRegistrations", "duration"], payload, self.log)
        return self.__send_request('post', self.path_register_context, self.headers, payload)

    def convenience_register_context(self, entity_id, payload, attribute_id=None, entity_type=None):
        """
        Register a context provider
        :param entity:
        :param payload:
        :param attribute_id:
        :param attribute_type:
        :return:
        The format is:
        {
          "duration" : "P1M",
          "providingApplication" : "http://mysensors.com/Rooms"
        }
        """
        check_valid_json(payload)
        check_minimal_attrs_payload(['duration', 'providingApplication'], payload, self.log)
        # Build url
        # If there is entity type --> /type/<type>/id/<id/attribute
        if entity_type is not None:
            url = '{convenience}/type/{entity_type}/id/{entity_id}/attributes/{atrribute_id}'.format(
                convenience=self.path_convenience, entity_type=entity_type, entity_id=entity_id,
                attribute_id=attribute_id)
        else:
            # If there is no entity type, the url has always the entity_id
            url_temp = '{convenience}/{entity_id}'.format(convenience=self.path_convenience, entity_id=entity_id)
            # If the attribute is specified --> /entity_id/attribute_id
            if attribute_id is not None:
                url = '{url_temp}/attributes/{attribute_id}'.format(url_temp=url_temp, attribute_id=attribute_id)
            else:
                url = url_temp

        return self.__send_request('post', url, self.headers, payload)

    def discover_context_availability(self, payload):
        """
        Discover the Context Providers for an entity in a service
        :param payload:
        :param subservice:
        :param service:
        :return:
        The format is:
        {
            "entities": [
                {
                    "type": "Room",
                    "isPattern": "false",
                    "id": "Room1"
                }
            ]
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["entities"], payload, self.log)
        return self.__send_request('post', self.path_discover_context_availability, self.headers, payload)

    def convenience_discover_context_availability(self, entity_id=None, entity_type=None, attribute_id=None):
        """
        Convenience discover the Context Providers
        /contextEntities/<entity_id>*
        /contextEntities/type/<entity_type>/id/<entity_id>*
        /contextEntities/<entity_id>/attributes/<attribute_id>*
        /contextEntities/type/<entity_type>/id/<entity_id>/attributes/<attribute_id>*
        /contextEntityTypes/<entity_type>
        /contextEntityTypes/<entity_type>/attributes/<attribute_id>
        :param entity_id:
        :param entity_type:
        :param attribute_id:
        :return:
        """
        # Build url
        if entity_id is not None and entity_type is not None and attribute_id is not None:
            # /contextEntities/type/<entity_type>/id/<entity_id>/attributes/<attribute_id>
            url = '{convenience}/type/{entity_type}/id/{entity_id}/attributes/{attribute_id}'.format(
                convenience=self.path_convenience, entity_type=entity_type, entity_id=entity_id,
                attribute_id=attribute_id)
        else:
            if entity_type is None:
                url_temp = '{convenience}/{entity_id}'.format(convenience=self.path_convenience)
                if attribute_id is not None:
                    # /contextEntities/<entity_id>/attributes/<attribute_id>
                    url = '{url_temp}/attributes/{attribute_id}'.format(url_temp=url_temp, attribute_id=attribute_id)
                else:
                    # /contextEntities/<entity_id>
                    url = url_temp
            else:
                if entity_id is not None:
                    # /contextEntities/type/<entity_type>/id/<entity_id>
                    url = '{convenience}/type/{entity_type}/id/{entity_id}'.format(convenience=self.path_convenience,
                                                                                   entity_type=entity_type,
                                                                                   entity_id=entity_id)
                else:
                    if attribute_id is None:
                        # /contextEntityTypes/<entity_type>
                        url = '{convenience_types}/{entity_type}'.format(convenience_types=self.path_convenience_types,
                                                                         entity_type=entity_type)
                    else:
                        # /contextEntityTypes/<entity_type>/attributes/<attribute_id>
                        url = '{convenience_types}/{entity_type}/attributes/{attribute_id}'.format(
                            convenience_types=self.path_convenience_types, entity_type=entity_type,
                            attribute_id=attribute_id)

        return self.__send_request('get', url, self.headers)

    def update_context_registration(self, payload):
        """
        Calls the registration_context but with a registrationId parameter in the payload
        :param payload:
        :param service:
        :param subservice:
        :return:
        The format is:
        {
            "contextRegistrations": [
                {
                    "entities": [
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room1"
                        },
                        {
                            "type": "Room",
                            "isPattern": "false",
                            "id": "Room2"
                        }
                    ],
                    "attributes": [
                        {
                            "name": "temperature",
                            "type": "float",
                            "isDomain": "false"
                        },
                        {
                            "name": "pressure",
                            "type": "integer",
                            "isDomain": "false"
                        }
                    ],
                    "providingApplication": "http://mysensors.com/Rooms"
                }
            ],
            "duration": "P1M",
            "registrationId": "aaaa"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["registrationId", "duration", "contextRegistrations"], payload, self.log)
        return self.register_context(payload)

    def subscribe_context_availability(self, payload):
        """
        Subscribe the Context Availability
        :param payload:
        :param subservice:
        :param service:
        :return:
        The format of the payload is:
        {
            "entities": [
            {
                "type": "Room",
                "isPattern": "true",
                "id": ".*"
            }
            ],
            "attributes": [
            "temperature"
            ],
            "reference": "http://localhost:1028/accumulate",
            "duration": "P1M"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["entities", "attributes", "reference", "duration"], payload, self.log)
        return self.__send_request('post', self.path_subscribe_context_availability, self.headers, payload)

    def convenience_subscribe_context_availability(self, payload):
        """
        Subscribe the Context Availability
        :param payload:
        :param subservice:
        :param service:
        :return:
        The format of the payload is:
        {
            "entities": [
            {
                "type": "Room",
                "isPattern": "true",
                "id": ".*"
            }
            ],
            "attributes": [
            "temperature"
            ],
            "reference": "http://localhost:1028/accumulate",
            "duration": "P1M"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["entities", "attributes", "reference", "duration"], payload, self.log)
        return self.__send_request('post', self.path_convenience_context_availability, self.headers, payload)

    def update_context_availability_subscription(self, payload):
        """
        Update the Context availability
        :param payload:
        :param subservice:
        :param service:
        :return:
        The format of the payload is:
        {
            "entities": [
            {
                "type": "Car",
                "isPattern": "true",
                "id": ".*"
            }
            ],
            "attributes": ["temperature"]
            "duration": "P1M",
            "subscriptionId": "52a745e011f5816465943d59"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["entities", "attributes", "subscriptionId", "duration"], payload, self.log)
        return self.__send_request('post', self.path_update_context_availability_subscription, self.headers, payload)

    def convenience_update_context_availability_subscription(self, payload):
        """
        Convenience update the Context availability
        Same as standard but in the url hast to go the subscription id, the same than in the payload
        :param payload:
        :param subservice:
        :param service:
        :return:
        The format of the payload is:
        {
            "entities": [
            {
                "type": "Car",
                "isPattern": "true",
                "id": ".*"
            }
            ],
            "attributes": ["temperature"]
            "duration": "P1M",
            "subscriptionId": "52a745e011f5816465943d59"
        }
        """

        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["entities", "attributes", "subscriptionId", "duration"], payload, self.log)
        url = '{convenience_context_availability}/{subscription_id}'.fromat(
            convenience_context_availability=self.path_convenience_context_availability,
            subscription_id=payload['subscriptionId'])
        return self.__send_request('put', url, self.headers, payload)

    def unsubscribe_context_availability(self, payload):
        """
        Unsubscribe the Context Availability
        :param payload:
        :param subservice:
        :param service:
        :return:
        The format of the payload is:
        {
            "subscriptionId": "52a745e011f5816465943d59"
        }
        """
        if self.check_json:
            payload = check_valid_json(payload)
            check_minimal_attrs_payload(["subscriptionId"], payload, self.log)
        return self.__send_request('post', self.path_unsubscribe_context_availability, self.headers, payload)

    def convenience_unsubscribe_context_availability(self, subscription_id):
        """
        Convenience unsubscribe the Context Availability
        :param payload:
        :param subservice:
        :param service:
        :return:
        """
        url = '{convenience_context_availability}/{subscription_id}'.fromat(
            convenience_context_availability=self.path_convenience_context_availability,
            subscription_id=subscription_id)
        return self.__send_request('delete', url, self.headers)

    def version(self):
        """
        Check the version of the CB
        :return:
        """
        return self.__send_request('get', self.path_version)


class CBUtils(object):
    """
    Basic functionality for ContextBroker
    """

    def __init__(self, instance,
                 protocol="http",
                 port="1026",
                 path_context="/v1/contextEntities",
                 path_query="/v1/queryContext",
                 path_statistics="/statistics",
                 path_subscription="/v2/subscriptions",
                 path_update="/v1/updateContext",
                 path_version="/version",
                 verbosity=0,
                 default_headers={"Accept": "application/json", 'content-type': 'application/json'}):
        """
        CB Utils constructor
        :param instance: ip of ContextBroker
        :param protocol: http/https
        :param port: 1026 by default
        :param path_context:
        :param path_query:
        :param path_statistics:
        :param path_subscription:
        :param path_update:
        :param path_version:
        :param verbosity: 1 by default [0 Silent, 1 Basic, 2 Complete, 3 Debug]
        """
        # initialize logger
        self.log = get_logger('cb_utils', verbosity)

        # Assign the values
        self.default_endpoint = protocol + '://' + instance + ':' + port
        self.default_headers = default_headers
        self.default_payload = None
        self.instance = instance
        self.protocol = protocol
        self.port = port
        self.path_context = path_context
        self.path_query = path_query
        self.path_statistics = path_statistics
        self.path_subscription = path_subscription
        self.path_update = path_update
        self.path_version = path_version
        self.verbosity = verbosity

    # TODO: Implement ngsi10 - Unsuscribe
    # TODO: Implement ngsi9

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
            try:
                parameters.update({'data': json.dumps(payload)})
            except ValueError:
                parameters.update({'data': payload})

        if query is not None:
            parameters.update({'params': query})

        if verify is not None:
            parameters.update({'verify': verify})

        # Send the requests
        try:
            response = requests.request(**parameters)
        except RequestException, e:
            PqaTools.log_requestAndResponse(url=url, headers=headers, data=payload, comp='CB', method=method)
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)

        # Log data
        PqaTools.log_fullRequest(comp='CB', response=response, params=parameters)

        return response

    def version(self):
        """
        Get CB version
        """
        headers = self.default_headers
        url = self.default_endpoint + self.path_version

        # send the request for the subscription
        response = self.__send_request('get', url, headers)
        return response

    def statistics(self):
        """
        Get CB statistics
        """
        headers = dict(self.default_headers)
        url = self.default_endpoint + self.path_statistics

        # send the request for the subscription
        response = self.__send_request('get', url, headers)
        return response

    def entity_get(self, service, entity_id, subservice=''):
        """
        Recover a CB entity
        """
        # set the service header id
        headers = dict(self.default_headers)
        headers.update({"Fiware-Service": service})
        headers.update({"Fiware-ServicePath": '/' + subservice})

        # set the endpoint of CB
        url = self.default_endpoint + self.path_context + '/' + entity_id

        # send the request for the subscription
        response = self.__send_request('get', url, headers)
        return response

    def entities_get(self, service, entity, entity_id, pattern='false', subservice=''):
        """
        Recover a CB entity
        """
        # set the service header id
        headers = dict(self.default_headers)
        headers.update({"Fiware-Service": service})
        headers.update({"Fiware-ServicePath": '/' + subservice})

        # set the endpoint of CB
        url = self.default_endpoint + self.path_query

        # build the payload
        template = """{"entities": [{"type": "{{ent_type}}","isPattern": "{{ent_pattern}}","id": "{{ent_id}}"} ]}"""
        payload = pystache.render(template,
                                  {'ent_type': entity,
                                   'ent_pattern': pattern,
                                   'ent_id': entity_id,
                                   })
        # send the request for the subscription
        response = self.__send_request('post', url, headers, json.loads(payload))
        return response

    def entity_append(self, service, entity_data, subservice=''):
        """
        Create if not exist a CB entity or update it
        Usage:
        entityData = {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]}

        entity_append('serviceID', entityData)
        """
        # set the service header id
        headers = dict(self.default_headers)
        headers.update({"Fiware-Service": service})
        headers.update({"Fiware-ServicePath": '/' + subservice})

        # set the endpoint of CB
        url = self.default_endpoint + self.path_update

        # load Template
        template = template_CB_EntityUpdate

        # fill the template with the values
        payload = pystache.render(template, {'ent_type': entity_data['ent_type'],
                                             'ent_pattern': entity_data['ent_pattern'],
                                             'ent_id': entity_data['ent_id'],
                                             'ent_attributes': entity_data['attributes'],
                                             'action_mode': 'APPEND'})

        # format avoid urlencoding due to not array inputs
        payload = payload.replace("'", '"')
        payload = payload.replace("u&quot;", '"')
        payload = payload.replace("&quot;", '"')

        # send the request for the subscription
        response = self.__send_request('post', url, headers, json.loads(payload))
        return response

    def entity_update(self, service, entity_data, subservice=''):
        """
        Create if not exist a CB entity or update it
        Usage:
        entityData = {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]}

        entity_update('serviceID', entityData)
        """
        # set the service header id
        headers = dict(self.default_headers)
        headers.update({"Fiware-Service": service})
        headers.update({"Fiware-ServicePath": '/' + subservice})

        # set the endpoint of CB
        url = self.default_endpoint + self.path_update

        # load Template
        template = template_CB_EntityUpdate

        # fill the template with the values
        payload = pystache.render(template, {'ent_type': entity_data['ent_type'],
                                             'ent_pattern': entity_data['ent_pattern'],
                                             'ent_id': entity_data['ent_id'],
                                             'ent_attributes': entity_data['attributes'],
                                             'action_mode': 'APPEND'})

        # format avoid urlencoding due to not array inputs
        payload = payload.replace("'", '"')
        payload = payload.replace("u&quot;", '"')
        payload = payload.replace("&quot;", '"')

        # send the request for the subscription
        response = self.__send_request('post', url, headers, json.loads(payload))
        return response

    def subscription_add(self, service, template_data={}, verifySSL=False, subservice=''):
        """
        Collect all the input data and mix it with the template to send

        templateData is a dict that can include 0..n of this params:
        {ent_type, ent_pattern, ent_id, notify_url, duration, subs_type, ent_att_cond}

        Usage example:
        templateData = dict({"ent_type": "Car","ent_pattern": "false", "notify_url": "http://localhost:5050/notify"})
        CBUtils.add_subscription('Service1',templateData=template)
        """
        # show info received
        if self.verbosity >= 2:
            print "###> INPUT > {}".format(template_data)

        # set the service header  id
        headers = dict(self.default_headers)
        headers.update({"Fiware-Service": service})
        headers.update({"Fiware-ServicePath": '/' + subservice})

        # set the endpoint of CB
        url = self.default_endpoint + self.path_subscription

        # set the default parameters parameters if not provided
        if 'notify_url' not in template_data:
            template_data['notify_url'] = 'http://127.0.0.1:5050/notify'
        if 'ent_type' not in template_data:
            template_data['ent_type'] = 'Room'
        if 'ent_pattern' not in template_data:
            template_data['ent_pattern'] = 'false'
        if 'ent_id' not in template_data:
            template_data['ent_id'] = 'Room99'
        if 'duration' not in template_data:
            template_data['duration'] = 'PT5M'
        if 'subs_type' not in template_data:
            template_data['subs_type'] = 'ONCHANGE'
        if 'ent_att_cond' not in template_data:
            template_data['ent_att_cond'] = ["temperature"]
        if 'ent_att_notif' not in template_data:
            template_data['ent_att_notif'] = ["temperature"]

        # Load template
        template = template_CB_SubscriptionUpdate

        # fill the template with the values
        # template = open('templates/cbSubscription.json', 'r')
        payload = pystache.render(template,
                                  {'ent_type': template_data['ent_type'],
                                   'ent_pattern': template_data['ent_pattern'],
                                   'ent_id': template_data['ent_id'],
                                   'notify_url': template_data['notify_url'],
                                   'duration': template_data['duration'],
                                   'subs_type': template_data['subs_type'],
                                   'ent_att_notif': template_data['ent_att_notif'],
                                   'ent_att_cond': template_data['ent_att_cond']})
        payload = payload.replace("'", '"')
        # send the request for the subscription
        return self.__send_request('post', url, headers, json.loads(payload), verifySSL)

    def get_attribute_value(self, service, entity_id, attribute_name, subservice=''):
        """
        Returns the value of an attribute given  the entity and the attribute name
        :param service: service
        :param entity_id: id of the entity
        :param attribute_name: name of the attribute
        :param subservice: subservice
        :return: None if the attribute does noy exist or if the entity does not exists, otherwise it returns the value
        of the attribute
        """
        # Get the entity
        response = self.entity_get(service, entity_id, subservice=subservice)
        assert response.status_code == 200, 'ERROR, entity cannot be retrieved'
        resp = None
        # Go through the response to find out the attribute value
        try:
            attributes_list = response.json()['contextElement']['attributes']
            for attribute in attributes_list:
                if attribute['name'] == attribute_name:
                    resp = attribute['value']
                    break
            return resp
        except KeyError:
            return resp

    def set_auth_token(self, auth_token):
        self.default_headers['x-auth-token'] = auth_token


if __name__ == '__main__':
    cb = CbNgsi10Utils('localhost', 'orion')
    attr = AttributesCreation()
    attr.add_attribute('Temperature', "celsius", '5')
    ce = ContextElements()
    ce.add_context_element('Room1', 'Room', attr)
    payload = PayloadUtils.build_standard_entity_creation_payload(ce)
    print payload
    resp = cb.standard_entity_creation(payload)
    print resp
    print resp.text
    print resp.headers
