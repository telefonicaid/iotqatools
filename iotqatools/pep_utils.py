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

from iotqatools.cb_utils import CBUtils
from iotqatools.ks_utils import KeystoneUtils
from iotqatools.ac_utils import AC
from iotqatools.iot_logger import get_logger


class Pep(object):
    """
    Class to manage the Pep
    """

    log = get_logger('Pep')

    def __init__(self, ip, port='1026', protocol='http'):
        self.url = '%s://%s:%s' % (protocol, ip, port)
        self.port = port
        self.protocol = protocol
        self.ip = ip

    def request_cb_operation(self, username, password, service, subservice, cb_method, cb_method_kwargs):
        self.log.info('Getting token')
        token = KeystoneUtils.get_token(username, password, service, ip=self.ip).headers
        self.log.debug('The token is: %s' % token)
        self.log.info('Creating the headers')

        headers = {
            "Accept": "application/json",
            'content-type': 'application/json',
            'Fiware-Servicepath': '/' + str(subservice),
            'X-Auth-Token': token['x-subject-token']
        }
        self.log.debug('The headers are: %s' % headers)
        self.log.info('Executing the method %s of \'cbUtils\'' % cb_method)
        self.log.debug('The info of the \'cbUtils\' arguments are: %s' % cb_method_kwargs)
        cb = CBUtils(self.ip, port=self.port, default_headers=headers, verbosity=2)
        cb_func = getattr(cb, cb_method)
        return cb_func(**cb_method_kwargs)


if __name__ == '__main__':
    ##############An example of how to use**********
    # IDM info
    platform = {
        'GlobalServiceAdmin': {
            'user': 'admin',
            'password': 'admin',
            'roles': ['admin', '_member_'],
            'domain': 'Default',
            'project': 'admin'
        },
        'RegionalServiceAdmin': {
            'user': 'cloud_admin',
            'password': 'password'
        },
        'address': {
            'ip': '127.0.0.1',
            'port': '5000'
        },
        'pep': {
            'user': 'pep',
            'password': 'pep',
            'mail': 'pep@no.com',
            'roles': ['service', '_member_']
        },
        'cloud_domain': {
            'name': 'admin_domain'
        },
        'admin_rol': {
            'name': 'admin'
        }
    }
    # Environment to deploy in KS
    environment = {
        'domains': [
            {
                'name': 'atlantic',
                'description': 'All the atlantic Ocean',
                'domain_admin': {
                    'username': 'white_shark',
                    'password': 'white_shark'
                },
                'users': [
                    {
                        'name': 'octopus',
                        'password': 'octopus',
                        'description': 'Tentacles guy',
                        'roles': [
                            {
                                'name': 'SubServiceAdmin'
                            }
                        ],
                        'projects': [
                            {
                                'name': '/coral',
                                'description': 'Nemos house',
                                'roles': [
                                    {
                                        'name': 'Customer'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
        ]
    }
    # Set IDM environment
    try:
        KeystoneUtils.prepare_environment(platform, environment)
    except KeyError:
        KeystoneUtils.clean_service(platform, 'atlantic')
        KeystoneUtils.prepare_environment(platform, environment)
    structure = KeystoneUtils.get_structure(platform)
    # Set AC environmebnt
    ac = AC('127.0.0.1')
    customer_role_id = structure['atlantic']['projects']['/coral']['users']['octopus']['roles']['Customer']['id']
    ac.create_policy('atlantic', customer_role_id, 'Customer_write', 'fiware:orion:atlantic:/coral::', 'create')
    # Set pep environment
    pep = Pep('127.0.0.1', '1025')
    entity_data = {
        "ent_type": "Car",
        "ent_pattern": "false",
        "ent_id": "Car01",
        "attributes": [{"name": "temperature", "type": "centigrade", "value": "99"}]
    }
    print pep.request_cb_operation('octopus', 'octopus', 'atlantic', 'coral', 'entity_append',
                                   {'service': 'atlantic', 'entity_data': entity_data})
