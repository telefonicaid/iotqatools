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

template_CB_EntityUpdate = """{
        "contextElements": [
            {
                "type": "{{ent_type}}",
                "isPattern": "{{ent_pattern}}",
                "id": "{{ent_id}}",
                "attributes": {{ent_attributes}}
            }],
        "updateAction": "{{action_mode}}"
    }"""

template_CB_SubscriptionUpdate = """{
        "entities": [
            {
                "type": "{{ent_type}}",
                "isPattern": "{{ent_pattern}}",
                "id": "{{ent_id}}"
            }
        ],
        "attributes": {{ent_att_notif}},
        "reference": "{{notify_url}}",
        "duration": "{{duration}}",
        "notifyConditions": [
            {
                "type": "{{subs_type}}",
                "condValues":
                    {{ent_att_cond}}
            }
        ]
    }"""
