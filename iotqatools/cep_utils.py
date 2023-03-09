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

import yaml
import pystache
import requests

from iotqatools.templates.cep_templates import *
from iotqatools.helpers_utils import *
from iotqatools.iot_logger import get_logger
from iotqatools.iot_tools import PqaTools
from requests.exceptions import RequestException


__logger__ = get_logger("cep_steps", 'DEBUG', True)

class CEP:
    """
    Manage Perseo requests / responses.
    """

    def __init__(self, instance,
                 protocol="http",
                 port="9090",
                 path='/m2m/vrules',
                 cep_version='',
                 verbosity='DEBUG',
                 default_headers={'Accept': 'application/json'},
                 verify=False,
                 check_json=True):
        """
        constructor with values by default
        :param protocol: protocol to be used (e.g. http:// or https://)
        :param port: port
        :param path: path
        :param verbosity: level for debugging purposes
        :param default_headers: default headers for CEP requests
        :param instance: cep endpoint
        :param cep_version: cep version
        """
        # initialize logger
        self.log = get_logger('cep_utils', verbosity)

        # Assign the values
        self.default_endpoint = protocol + '://' + instance + ':' + port
        self.default_headers = default_headers
        self.instance = instance
        self.protocol = protocol
        self.port = port
        self.path = path
        self.version = cep_version
        self.headers = default_headers
        self.verify = verify
        self.check_json = check_json

    def __create_headers(self, service, subservice='', token=''):
        """
        create the header for different requests
        :param service: name of the service
        :param subservice: name of the subservice
        :return: headers dictionary
        """
        headers = dict(self.default_headers)
        headers.update({"Fiware-Service": service})
        headers.update({"Fiware-ServicePath": subservice})
        headers.update({"x-auth-token": token})
        return headers

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
                parameters.update({'data': payload.encode('utf-8')})

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
            PqaTools.log_requestAndResponse(url=url, headers=headers, params=query, data=payload, comp='CEP',
                                            method=method)
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)

        # Log data
        PqaTools.log_fullRequest(comp='CEP', response=response, params=parameters)

        return response

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


    # -------------------------- CARDS ------------------------------------------------------------
    def create_type_sensor_card(self, sc_id_card, parameter_value, operator, connected_to):
        """
        Create a new sensor card
        :param sc_id_card: Identifier used in connectedTo field
        :param parameter_value: value to verify
        :param operator: GREATER_THAN|MINOR_THAN|EQUAL_TO|GREATER_OR_EQUAL_THAN|MINOR_OR_EQUAL_THAN |DIFFERENT_TO
        :param connected_to: next card connected to this card. SHOULD BE A LIST
        :return: sensor card dictionary
        """
        # Load template
        template = template_CEP_SensorCard_type

        # fill the template with the values
        sensor_card = pystache.render(template,
                                      {'sc_id_card': sc_id_card,
                                       'parameter_value': parameter_value,
                                       'connected_to': connected_to,
                                       'operator': operator})
        sensor_card = sensor_card.replace("'", '"')
        return yaml.load(sensor_card)

    def create_id_sensor_card(self, sc_id_card, regexp, parameter_value, operator, connected_to):
        """
        Create a new sensor card
        :param regexp: regular expression for the entity id
        :param sc_id_card: Identifier used in connectedTo field
        :param parameter_value: value to verify
        :param operator: GREATER_THAN|MINOR_THAN|EQUAL_TO|GREATER_OR_EQUAL_THAN|MINOR_OR_EQUAL_THAN |DIFFERENT_TO
        :param connected_to: next card connected to this card. SHOULD BE A LIST
        :return: sensor card dictionary
        """
        # Load template
        template = template_CEP_SensorCard_regexp

        # fill the template with the values
        sensor_card = pystache.render(template,
                                      {'sc_id_card': sc_id_card,
                                       'regexp': regexp,
                                       'parameter_value': parameter_value,
                                       'connected_to': connected_to,
                                       'operator': operator})
        sensor_card = sensor_card.replace("'", '"')
        return yaml.load(sensor_card)

    def create_value_sensor_card(self, sc_id_card, attribute_name, attribute_data_type, parameter_value, operator,
                                 connected_to):
        """
        Create a new sensor card
        :param regexp: regular expression for the entity id
        :param sc_id_card: Identifier used in connectedTo field
        :param parameter_value: value to verify
        :param operator: GREATER_THAN|MINOR_THAN|EQUAL_TO|GREATER_OR_EQUAL_THAN|MINOR_OR_EQUAL_THAN |DIFFERENT_TO
        :param connected_to: next card connected to this card. SHOULD BE A LIST
        :return: sensor card dictionary
        """
        # Load template
        template = template_CEP_SensorCard_valueThreshold

        # fill the template with the values
        sensor_card = pystache.render(template,
                                      {'sc_id_card': sc_id_card,
                                       'attribute_name': attribute_name,
                                       'attribute_data_type': attribute_data_type,
                                       'parameter_value': parameter_value,
                                       'connected_to': connected_to,
                                       'operator': operator})
        sensor_card = sensor_card.replace("'", '"')
        return yaml.load(sensor_card)

    def create_action_card(self, ac_id_card, ac_name_card, action_type, ac_parameters, connected_to=[]):
        """
        Create an action card and adds it to the list of cards for creating rules
        :return : dict
        :param ac_id_card: id of the card
        :param ac_name_card: name of the card
        :param action_type: action type (EMAIL | SMS | UPDATECB)
        :param ac_parameters: a list of dicctionaries (e.g. [{"name": "parameter_name", "value": "parameter_value"}"] )
        :param connected_to: next cards. SHOULD be a list. By default an action card has no next card connected
        """
        # assert action_type == 'SendEmailAction' or action_type == 'SendSmsAction', \
        #    'WARN - ActionCard type is not allowed: {}'.format(action_type)

        # Load template
        template = template_CEP_ActionCard
        # fill the template with the values
        action_card = pystache.render(template,
                                      {'ac_id_card': ac_id_card,
                                       'ac_name_card': ac_name_card,
                                       'action_type': action_type,
                                       'userParams': ac_parameters,
                                       'connected_to': connected_to})
        action_card = action_card.replace("'", '"')
        return yaml.load(action_card)

    def create_visual_rule(self, rule_name, service, sensor_card_list, action_card_list, subservice='', active=1, token=''):
        """
        create a new card rule
        :param service: name of the service
        :param sensor_card_list: list of sensor cards. Must be a list
        :param action_card_list: list of action cards. Must be a list
        :param subservice: name of the subservice
        :param rule_name: rule name
        :param active: if is active or not (0 | 1)
        :return: response object
        """
        # assert len(rule_name) > 1024, 'WARN, the rule name {} is longer than 1024 chars'.format(rule_name)
        cards = []
        for sensor_card in sensor_card_list:
            cards.append(sensor_card)
        for action_card in action_card_list:
            cards.append(action_card)
        # Load template
        template = template_CEP_Rule
        # fill the template with the values

        cep_payload = pystache.render(template,
                                      {'rule_name': rule_name,
                                       'active': active,
                                       'cards': cards})
        headers = self.__create_headers(service, str(subservice), token)
        headers.update({'content-type': 'application/json'})

        cep_payload = cep_payload.replace("'", '"')
        url = self.default_endpoint + self.path
        return self.__send_request('post', url, payload=json.dumps(yaml.load(cep_payload)), headers=headers,
                                   verify=self.verify)

    def delete_visual_rule(self, rule_name, service, subservice='', token=''):
        """
        Delete a visual rule given the name, the service and the subservice
        :param rule_name: name of the rule
        :param service: name of the service
        :param subservice: name of the subservice
        :return: response object
        """
        headers = self.__create_headers(service, str(subservice), token)

        url = self.default_endpoint + self.path + '/' + rule_name
        return self.__send_request('delete', url, headers=headers, verify=self.verify)

    def get_visual_rule(self, rule_name, service, subservice=''):
        """
        Retrieves a viual rules given the id, service and subservice
        :param rule_name: name of the rule
        :param service: name of the service
        :param subservice: name of the subservice
        :return: response object with the rule data
        """
        headers = self.__create_headers(service, str(subservice))
        url = self.default_endpoint + self.path + '/' + rule_name
        return self.__send_request('get', url, headers=headers, verify=self.verify)

    def list_visual_rules(self, service, subservice=''):
        """
        Return the list of rules for a given service/subservice
        :param service: name of the service
        :param subservice: name of the subservice
        :return: response object with the list of rules
        """
        headers = self.__create_headers(service, str(subservice))
        url = self.default_endpoint + self.path
        return self.__send_request('get', url, headers=headers, verify=self.verify)

    def update_visual_rule(self, rule_name, parameter_list, service, subservice=''):
        """
        Updates the rule with the parameters specified
        :param rule_name: name of the rule
        :param parameter_list: list of parameters to be changed
        :param service: name of the service
        :param subservice: name of the subservice
        :return: response object
        """
        headers = self.__create_headers(service, str(subservice))
        url = self.default_endpoint + self.path + '/' + rule_name
        # TODO: device a way to map the parameters to the payload expected by the CEP
        rule_payload = parameter_list
        return self.__send_request('put', url, headers=headers, payload=rule_payload, verify=self.verify)

    # -------------------------- Plain rules ------------------------------------------------------------
    def __append_headers(self, **kwargs):
        """
        append headers for different requests
        kwargs fields:
        :param service: name of the service
        :param service_path: name of the subservice
        :param token:  token for getting access from Auth Server which can be used to get to a CEP behind a PEP.
        :return: headers dict
        """
        headers = self.default_headers
        service = kwargs.get("service", None)
        service_path = kwargs.get("service_path", None)
        token = kwargs.get("token", None)
        if service is not None:
            headers["Fiware-Service"] = service
        if service_path is not None:
            headers["Fiware-ServicePath"] = service_path
        if token is not None:
            headers["X-Auth-Token"] = token
        return headers

    def create_plain_rule(self, name, action, rule_properties):
        """
        create a plain rule using EPL statement used by the Esper engine inside perseo-core.

        :param name: name of the rule, used as identifier
        :param action: action to be performed by perseo if the rule is fired from the core
        :param rule_properties: rule properties. See below labels used:
          headers:
           - service: service used
           - service_path: service_path used
           - token: token for getting access from Auth Server which can be used to get to a CEP behind a PEP.
          epl:
           - attr_name: attribute name
           - attr_value: attribute value
           - attr_op: attribute operation used (> | < | >= | <= | = | <>)
           - meta_name: attribute metadata name or suffixes
           - meta_value: attribute metadata value
           - meta_op: attribute metadata operation used (> | < | >= | <= | = | <>)
           - id: entity id or idPattern
           - type: entity type or typePattern
           geo-location:
             - location_x: UTM easting coordinates are referenced to the center line of the zone known as the central meridian
             - location_y: UTM northing coordinates are measured relative to the equator                                                |
             - location_ratio: circle size (distance)
           timestamp:
             - timestamp_last_minutes: determine if the given timestamp is into the given last minutes
          actions:
           - update_name: mandatory, attribute name to set
           - update_value: mandatory, attribute value to set
           - update_id: optional, the id of the entity which attribute is to be updated (by default the id of the entity that triggers the rule is used, i.e. ${id})
           - update_type: optional, the type of the entity which attribute is to be updated (by default the type of the entity that triggers the rule is usedi.e. ${type})
           - update_ispattern: optional, false by default
           - update_attr_type: optional, type of the attribute to set. By default, not set (in which case, only the attribute value is changed).
           - update_trust: optional, trust token for getting an access token from Auth Server which can be used to get to a Context Broker behind a PEP.
           - http_method: optional, HTTP method to use, POST by default
           - http_url: mandatory, URL target of the HTTP method
           - http_headers: optional, an object with fields and values for the HTTP header
           - http_qs: optional, an object with fields and values to build the query string of the URL
           - http_json: optional, an object that will be sent as JSON. String substitution will be performed in the keys and values of the object's fields. If present, it overrides template from action
           - consumer_key: consumer key associated to the twitter user.
           - consumer_secret: consumer secret associated to the twitter user.
           - access_token_key: access token key associated to the twitter user.
           - access_token_secret: access token secret associated to the twitter user.
           - template: template used in sms, email, http and twitter actions
           - to: set of email address or phone number to send the message to. Used in sms and email actions
           - from: the sender email address or phone numbers. Used in sms and email actions
           - subject: subject of the email, used in email action
        :return http response
        :hint  some methods come from iotqatools.helpers_utils.py library
        """
        # text - epl
        text = u'select *, \"%s\" as ruleName, *, ev.%s? as %s, ev.id? as id from pattern [every ev=iotEvent(' % \
               (name, rule_properties["attr_name"], rule_properties["attr_name"])
        if "attr_value" in rule_properties:
            value, data_type = get_type_value(str(rule_properties["attr_value"]))
            text = u'%s cast(cast(%s?,String),%s)%s%s and' % \
                   (text, rule_properties["attr_name"], data_type, rule_properties["attr_op"], rule_properties["attr_value"])
        if "timestamp_last_minutes" in rule_properties: #timestamp
            #text = u'%s cast(cast(%s__ts?,String),float) > current_timestamp - %s*60*1000 and' % \
            #       (text, rule_properties["attr_name"], rule_properties["timestamp_last_minutes"])
            text = u'%s cast(cast(%s?,string), long, dateformat:\'iso\') > current_timestamp - %s*60*1000 and' % \
                   (text, rule_properties["attr_name"], rule_properties["timestamp_last_minutes"])
        if "location_x" in rule_properties:  # geo-location
            #text = u'%s Math.pow((cast(cast(%s__x?,String),float) - %s), 2) + Math.pow((cast(cast(%s__y?,String),float) - %s), 2) %s Math.pow(%s,2) and' % \
            #       (text, rule_properties["attr_name"], rule_properties["location_x"], rule_properties["attr_name"], rule_properties["location_y"], rule_properties["attr_op"], rule_properties["location_ratio"])
            text = u'%s Math.pow((cast(cast(cast(%s, java.util.Map).get(cast("coordinates",String)),java.util.ArrayList).get(0),float) - %s), 2) + Math.pow((cast(cast(cast(%s, java.util.Map).get(cast("coordinates",String)),java.util.ArrayList).get(1),float) - %s), 2) %s Math.pow(%s,2) and' % \
                   (text, rule_properties["attr_name"], rule_properties["location_x"], rule_properties["attr_name"], rule_properties["location_y"], rule_properties["attr_op"], rule_properties["location_ratio"])
            #text = u'%s true and' % \
            #       (text)
        if "meta_value" in rule_properties:
            value, data_type = get_type_value(str(rule_properties["meta_value"]))
            text = u'%s cast(cast(%s?,String),%s)%s%s and' % \
                   (text, rule_properties["meta_name"], data_type, rule_properties["meta_op"], rule_properties["meta_value"])
        if "type" in rule_properties:
            text = u'%s type=\"%s\" and' % (text, rule_properties["type"])
        if "id" in rule_properties:
            text = u'%s id=\"%s\" and' % (text, rule_properties["id"])
        if text[-4:] == " and": text = u'%s)]' % text[:-4]  # replace the last " and" by ")]"

        # action
        action_dict = {"type": action}
        action_dict["parameters"] = {}

        if action == "email":
            if "template" in rule_properties:
                action_dict["template"] = rule_properties["template"]
            if "to" in rule_properties:
                action_dict["parameters"]["to"] = rule_properties["to"]
            if "from" in rule_properties:
                action_dict["parameters"]["from"] = rule_properties["from"]
            if "subject" in rule_properties:
                action_dict["parameters"]["subject"] = rule_properties["subject"]

        elif action == "sms":
            if "template" in rule_properties:
                action_dict["template"] = rule_properties["template"]
            if "to" in rule_properties:
                action_dict["parameters"]["to"] = rule_properties["to"]

        # it is possible to updates one or more attributes of a given entity
        elif action == "update":
            if "update_id" in rule_properties:
                action_dict["parameters"]["id"] = rule_properties["update_id"]
            if "update_type" in rule_properties:
                action_dict["parameters"]["type"] = rule_properties["update_type"]
            if "update_ispattern" in rule_properties:
                action_dict["parameters"]["isPattern"] = rule_properties["update_ispattern"]
            if "update_trust" in rule_properties:
                action_dict["parameters"]["trust"] = rule_properties["update_trust"]
            # one or more attributes
            action_dict["parameters"]["attributes"] = []
            attrs_name_list = rule_properties["update_name"].split("&")
            attrs_value_list = rule_properties["update_value"].split("&")
            attrs_type_list = []
            #_attribute type is optional
            if "update_attr_type" in rule_properties:
                while rule_properties["update_attr_type"].find("&&") >= 0:
                    rule_properties["update_attr_type"] = rule_properties["update_attr_type"].replace("&&", '&none&')
                attrs_type_list = convert_str_to_list(rule_properties["update_attr_type"],"&")
            for i in range(len(attrs_name_list)):
                attr = {}
                attr["name"] = attrs_name_list[i]
                attr["value"] = attrs_value_list[i]
                if (len(attrs_type_list) > i) and (attrs_type_list[i] != "none"):
                    attr["type"] = attrs_type_list[i]
                action_dict["parameters"]["attributes"].append(attr)

        elif action == "post":
            action_dict["parameters"]["url"] = rule_properties["http_url"]
            if "http_json" in rule_properties:
                action_dict["parameters"]["json"] = convert_str_to_dict(rule_properties["http_json"], "json")
            else:
                if "template" in rule_properties:
                    action_dict["template"] = rule_properties["template"]
            if "http_method" in rule_properties:
                action_dict["parameters"]["method"] = rule_properties["http_method"]
            if "http_headers" in rule_properties:
                action_dict["parameters"]["headers"] = convert_str_to_dict(rule_properties["http_headers"], "json")
            if "http_qs" in rule_properties:
                action_dict["parameters"]["qs"] = convert_str_to_dict(rule_properties["http_qs"], "json")

        elif action == "twitter":
            action_dict["template"] = rule_properties["template"]
            action_dict["consumer_key"] = rule_properties["consumer_key"]
            action_dict["consumer_secret"] = rule_properties["consumer_secret"]
            action_dict["access_token_key"] = rule_properties["access_token_key"]
            action_dict["access_token_secret"] = rule_properties["access_token_secret"]
        else:
            __logger__.warn("the %s action does not exist..." % action)

        #rule
        rule = {"name": name,
                "text": text,
                "action": action_dict}
        payload = convert_dict_to_str(rule, "json")

        # headers
        headers = {}
        if "service" in rule_properties:
            headers = self.__append_headers(service=rule_properties["service"])
        if "service_path" in rule_properties:
            headers = self.__append_headers(service_path=rule_properties["service_path"])
        if "token" in rule_properties:
            headers = self.__append_headers(token=rule_properties["token"])

        headers.update({'content-type': 'application/json'})

        # url
        url = "%s/rules" % self.default_endpoint

        # request
        return self.__send_request('post', url, payload=payload, headers=headers, verify=self.verify)

    def delete_plain_rule(self, name, rule_properties):
        """
        delete the plain rule with a given name
        :param name: rule name to delete
        :param rule_properties: rule properties. See below labels used:
          headers:
           - service: service used
           - service_path: service_path used
           - token: token for getting access from Auth Server which can be used to get to a CEP behind a PEP.
        :return http response
        """
        # headers
        headers = {}
        if "service" in rule_properties:
            headers = self.__append_headers(service=rule_properties["service"])
        if "service_path" in rule_properties:
            headers = self.__append_headers(service_path=rule_properties["service_path"])
        if "token" in rule_properties:
            headers = self.__append_headers(token=rule_properties["token"])

        # url
        url = "%s/rules/%s" % (self.default_endpoint, name)

        # request
        return self.__send_request('delete', url, headers=headers, verify=self.verify)
