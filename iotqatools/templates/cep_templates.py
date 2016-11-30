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

template_CEP_SensorCard_type = """{
                            "id": "{{sc_id_card}}",
                            "type": "SensorCard",
                            "sensorCardType": "type",
                            "sensorData": {
                                "dataType": "Text",
                            },
                            "configData": {},
                            "connectedTo": {{connected_to}},
                            "conditionList": [
                                {
                               "scope": "XPATH",
                               "parameterValue": "{{parameter_value}}",
                               "parameterName": "type",
                               "not": false,
                               "operator": "{{operator}}",
                               "userProp": ""
                                }
                            ]
                            }"""

template_CEP_SensorCard_regexp = """{
                            "id": "{{sc_id_card}}",
                            "type": "SensorCard",
                            "sensorCardType": "regexp",
                            "sensorData": {
                                "parameterValue": "{{regexp}}"
                            },
                            "configData": {},
                            "connectedTo": {{connected_to}},
                            "conditionList": [
                                {
                               "scope": "XPATH",
                               "parameterValue": "{{parameter_value}}",
                               "parameterName": "id",
                               "not": false,
                               "operator": "{{operator}}",
                               "userProp": "{{regexp}}"
                                }
                            ]
                            }"""

template_CEP_SensorCard_valueThreshold = """{
                            "id": "{{sc_id_card}}",
                            "type": "SensorCard",
                            "sensorCardType": "valueThreshold",
                            "sensorData": {
                                "measureName": "{{attribute_name}}",
                                "phenomenon": "",
                                "phenomenonApp": "",
                                "dataType": "{{attribute_data_type}}",
                                "uom": ""
                            },
                            "connectedTo": {{connected_to}},
                            "conditionList": [
                                {
                               "scope": "OBSERVATION",
                               "parameterValue": "{{parameter_value}}",
                               "not": false,
                               "operator": "{{operator}}"
                                }
                            ]
                            }"""


template_CEP_ActionCard = """{
                             "id": "{{ac_id_card}}",
                             "type": "ActionCard",
                             "actionData": {
                                "name": "{{ac_name_card}}",
                                "type": "{{action_type}}",
                                "userParams": {{userParams}}
                              },
                             "connectedTo": {{connected_to}}
                             }"""

template_CEP_Rule="""{
    "name": "{{rule_name}}",
    "active": {{active}},
    "cards": {{cards}}
}"""