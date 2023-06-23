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
        self.path_update_entity = "{}{}".format(self.default_endpoint, path_entities_id_attrs)
        self.path_context_subscriptions = "{}{}".format(self.default_endpoint, path_subscriptions)
        self.path_context_subscriptions_by_id = "{}{}".format(self.default_endpoint, path_subscriptions_id)
        self.path_version = path_version
        self.verify = verify
        self.check_json = check_json

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

    def list_entities(self, headers={}, filters=None):
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

        # Set the filters of the requests as params
        if filters is not None:
            params = filters
        else:
            params = None

        return self.__send_request('get', self.path_entities, headers=headers, verify=None, query=params)

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

    def retrieve_subscriptions(self, headers, options=None):
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
        return self.__send_request('get', self.path_context_subscriptions, headers=headers, verify=None, query=options)

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
        path = self.path_context_subscriptions_by_id.replace('subscriptionId', subscription_id)

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
        path = self.path_context_subscriptions

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
        path = self.path_context_subscriptions_by_id.replace('subscriptionId', sub_id)

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
