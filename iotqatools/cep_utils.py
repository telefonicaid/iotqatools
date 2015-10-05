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

import yaml
import pystache
import requests
import json

from iotqatools.iot_logger import get_logger
from iotqatools.templates.cep_templates import *


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
                 default_headers={'Accept': 'application/json', 'content-type': 'application/json'}):
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

    def create_visual_rule(self, rule_name, service, sensor_card_list, action_card_list, subservice='', active=1):
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
        headers = self.__create_headers(service, str(subservice))

        cep_payload = cep_payload.replace("'", '"')
        url = self.default_endpoint + self.path
        print url
        print json.dumps(yaml.load(cep_payload))
        response = requests.post(url, data=json.dumps(yaml.load(cep_payload)), headers=headers, verify=False)
        assert response.status_code == 201, 'ERROR {}, the rule {} cannot be created. {}'.format(response.status_code,
                                                                                                 rule_name,
                                                                                                 response.text)
        return response

    def delete_visual_rule(self, rule_name, service, subservice=''):
        """
        Delete a visual rule given the name, the service and the subservice
        :param rule_name: name of the rule
        :param service: name of the service
        :param subservice: name of the subservice
        :return: response object
        """
        headers = self.__create_headers(service, str(subservice))
        url = self.default_endpoint + self.path + '/' + rule_name
        response = requests.delete(url, headers=headers, verify=False)
        assert response.status_code == 204, 'ERROR {}, the rule {}, cannot be deleted. {}'.format(response.status_code,
                                                                                                  rule_name,
                                                                                                  response.text)
        return response

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
        response = requests.get(url, headers=headers, verify=False)
        assert response.status_code == 200, 'ERROR, the rule {} cannot be retrieved'.format(rule_name)
        return response

    def list_visual_rules(self, service, subservice=''):
        """
        Return the list of rules for a given service/subservice
        :param service: name of the service
        :param subservice: name of the subservice
        :return: response object with the list of rules
        """
        headers = self.__create_headers(service, str(subservice))
        url = self.default_endpoint + self.path
        response = requests.get(url, headers=headers, verify=False)
        assert response.status_code == 200, 'ERROR, the list of rules cannot be retrieved'
        return response

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
        response = requests.put(url, headers=headers, data=rule_payload, verify=False)
        assert response.status_code == 200, 'ERROR, the rule {} cannot be updated'.format(rule_name)
        return response
