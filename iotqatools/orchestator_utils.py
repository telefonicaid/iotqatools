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

__author__ = 'avega'

import json
import requests

from iotqatools.iot_tools import get_logger
from iotqatools.iot_tools import PqaTools
from iotqatools.ks_utils import KeystoneUtils

class Orchestrator(object):
    """
    Class to manage Orchestrator
    """
    BASE_PATH_MANAGE = '/v1.0/'

    log = get_logger('Orchestrator', 'ERROR')

    def __init__(self, host='127.0.0.1', port='8084', protocol='http', verify=False, ks_host='127.0.0.1', ks_port='5001'):
        self.url = '%s://%s:%s' % (protocol, host, port)
        self.ip = host
        self.verify = verify
        self.timeout = 120 # should be greather than harakiri orc option
        self.ks_host = ks_host
        self.ks_port = ks_port

    def send(self, method, url, headers=None, payload=None, query=None, verify=None):
        """
        Funtion to send requests printing data to send by log
        :param method: get, post, delete, patch, update...
        :param url:
        :param headers:
        :param payload:
        :param query:
        :param verify:
        :return: response object
        """

        request_parms = {}
        if headers is not None:
            request_parms.update({'headers': headers})
        if payload is not None:
            request_parms.update({'data': payload})
        if query is not None:
            request_parms.update({'params': query})
        if verify is not None:
            request_parms.update({'verify': verify})
        else:
            # If the method does not include the verify parameter, it takes the value from object
            request_parms.update({'verify': self.verify})
        request_parms.update({'timeout': self.timeout})

        # Send the requests
        response = requests.request(method, url, **request_parms)

        # Log data
        PqaTools.log_fullRequest(comp='ORC', response=response, params=request_parms)

        return response

    def _get_service_id(self,
                        service_name,
                        admin_domain_user,
                        admin_domain_password):

        # Try get service_id as cloud_admin
        data = {
            "DOMAIN_NAME": "admin_domain",
            "SERVICE_ADMIN_USER": admin_domain_user,
            "SERVICE_ADMIN_PASSWORD": admin_domain_password,
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service'
        response = self.send('get', url_to_send, headers=headers,
                             payload=json_payload)

        json_response = json.loads(response.content)
        if 'domains' in json_response:
            for domain in json_response['domains']:
                if domain['name'] == service_name:
                    return domain['id']
        else:
            # Try to get service_id as service admin by token
            service_id = KeystoneUtils.get_service_id(admin_domain_user,
                                                      admin_domain_password,
                                                      service_name,
                                                      ip=self.ks_host,
                                                      port=self.ks_port)
            if not isinstance(service_id, requests.Response):
                return service_id

        return None

    def create_new_service(self,
                           domain_admin_name,
                           domain_admin_user,
                           domain_admin_password,
                           new_service_name,
                           new_service_description,
                           new_service_admin,
                           new_service_admin_password,
                           new_service_admin_email):
        """
        Create a new service using orchestrator
        :param domain_admin_name
        :param domain_admin_user
        :param domain_admin_password
        :param new_service_name
        :param new_service_description
        :param new_service_admin
        :param new_service_admin_password
        :param new_service_admin_email
        :return:
        """
        data = {
            "DOMAIN_NAME": domain_admin_name,
            "DOMAIN_ADMIN_USER": domain_admin_user,
            "DOMAIN_ADMIN_PASSWORD": domain_admin_password,
            "NEW_SERVICE_NAME": new_service_name,
            "NEW_SERVICE_DESCRIPTION": new_service_description,
            "NEW_SERVICE_ADMIN_USER": new_service_admin,
            "NEW_SERVICE_ADMIN_PASSWORD": new_service_admin_password,
            "NEW_SERVICE_ADMIN_EMAIL": new_service_admin_email
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service'
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def remove_service(self,
                       service_name,
                       admin_domain_user,
                       admin_domain_password):
        """
        Delete a service using orchestrator
        :param service_name
        :param admin_domain_user
        :param admin_domain_password
        :return:
        """
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": admin_domain_user,
            "SERVICE_ADMIN_PASSWORD": admin_domain_password
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service'
        response = self.send('delete', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def create_new_subservice(self,
                              service_name,
                              service_id,
                              service_admin_user,
                              service_admin_password,
                              new_subservice_name,
                              new_subservice_description):
        """
        Create a new subservice using orchestrator
        :param service_name
        :param service_id
        :param service_admin_user
        :param service_admin_password
        :param new_subservice_name
        :param new_subservice_description
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "NEW_SUBSERVICE_NAME": new_subservice_name,
            "NEW_SUBSERVICE_DESCRIPTION": new_subservice_description
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/subservice/' % service_id
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)

        return response

    def remove_subservice(self,
                          service_name,
                          service_id,
                          service_admin_user,
                          service_admin_password,
                          subservice_name):
        """
        Create a new subservice using orchestrator
        :param service_name
        :param service_id
        :param service_admin_user
        :param service_admin_password
        :param service_name
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SUBSERVICE_NAME": subservice_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/subservice/' % service_id
        response = self.send('delete', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def create_new_service_user(self,
                                service_name,
                                service_admin_user,
                                service_admin_password,
                                new_service_user_name,
                                new_service_user_password,
                                new_service_user_email,
                                new_service_user_description,
                                service_id=None):
        """
        Create a new subservice using orchestrator
        :param service_name
        :param service_admin_user
        :param service_admin_password
        :param new_service_user_name
        :param new_service_user_password
        :param new_service_user_email
        :param new_service_user_description
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "NEW_SERVICE_USER_NAME": new_service_user_name,
            "NEW_SERVICE_USER_PASSWORD": new_service_user_password,
            "NEW_SERVICE_USER_EMAIL": new_service_user_email,
            "NEW_SERVICE_USER_DESSCRIPTION": new_service_user_description
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/user/' % service_id
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def remove_service_user(self,
                            service_name,
                            service_id,
                            service_admin_user,
                            service_admin_password,
                            user_name,
                            user_id):
        """
        Create a new subservice using orchestrator
        :param service_name
        :param service_admin_user
        :param service_admin_password
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "USER_NAME": user_name
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/user/%s' % (service_id, user_id)
        response = self.send('delete', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def create_new_service_role(self,
                                service_name,
                                service_id,
                                service_admin_user,
                                service_admin_password,
                                new_role_name):
        """
        Create a new role service using orchestrator
        :param service_name
        :param service_admin_user
        :param service_admin_password
        :param new_service_role
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "NEW_ROLE_NAME": new_role_name,
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/role/' % service_id
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def remove_service_role(self,
                            service_name,
                            service_id,
                            service_admin_user,
                            service_admin_password,
                            role_name,
                            role_id):
        """
        Create a new subservice using orchestrator
        :param service_name
        :param service_admin_user
        :param service_admin_password
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "ROLE_NAME": role_name,
            "NEW_ROLE_NAME": role_name,
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/role/%s' % (service_id, role_id)
        response = self.send('delete', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def assign_role_service_user(self,
                                 service_name,
                                 service_admin_user,
                                 service_admin_password,
                                 role_name,
                                 service_user_name,
                                 service_id=None):
        """
        Assign a role to a user in a service
        :param service_name
        :param service_admin_user
        :param service_admin_password
        :param role_name
        :param service_user_name
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "ROLE_NAME": role_name,
            "SERVICE_USER_NAME": service_user_name
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/role_assignments' % service_id
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def assign_role_subservice_user(self,
                                    service_name,
                                    subservice_name,
                                    service_admin_user,
                                    service_admin_password,
                                    role_name,
                                    service_user_name,
                                    service_id=None,
                                    inherit=False):
        """
        Assign a role to a user in a subservice
        :param service_name
        :param service_id
        :param subservice_name
        :param service_admin_user
        :param service_admin_password
        :param role_name
        :param service_user_name
        :param inherit
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SUBSERVICE_NAME": subservice_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "ROLE_NAME": role_name,
            "SERVICE_USER_NAME": service_user_name
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/role_assignments' % service_id
        if inherit:
            url_to_send += '?inherit=true'
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def unassign_role_service_user(self,
                                   service_name,
                                   service_id,
                                   service_admin_user,
                                   service_admin_password,
                                   role_name,
                                   service_user_name):
        """
        Unassign a role to a user in a service
        :param service_name
        :param service_admin_user
        :param service_admin_password
        :param role_name
        :param service_user_name
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "ROLE_NAME": role_name,
            "SERVICE_USER_NAME": service_user_name
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/role_assignments' % service_id
        response = self.send('delete', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def unassign_role_subservice_user(self,
                                      service_name,
                                      service_id,
                                      subservice_name,
                                      service_admin_user,
                                      service_admin_password,
                                      role_name,
                                      service_user_name):
        """
        Unassign a role to a user in a subservice
        :param service_name
        :param service_id
        :param subservice_name
        :param service_admin_user
        :param service_admin_password
        :param role_name
        :param service_user_name
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SUBSERVICE_NAME": subservice_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "ROLE_NAME": role_name,
            "SERVICE_USER_NAME": service_user_name
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/role_assignments' % service_id
        response = self.send('delete', url_to_send, headers=headers,
                             payload=json_payload)
        return response

    def create_trust_token(self,
                           service_name,
                           service_id,
                           subservice_name,
                           service_admin_user,
                           service_admin_password,
                           role_name,
                           trustee_user_name,
                           trustor_user_name):
        """
        Assign a role to a user in a subservice
        :param service_name
        :param service_id
        :param subservice_name
        :param service_admin_user
        :param service_admin_password
        :param role_name
        :param trustee_user_name
        :param trustor_user_name
        :return:
        """
        if not service_id:
            service_id = self._get_service_id(service_name,
                                              service_admin_user,
                                              service_admin_password)
        data = {
            "SERVICE_NAME": service_name,
            "SUBSERVICE_NAME": subservice_name,
            "SERVICE_ADMIN_USER": service_admin_user,
            "SERVICE_ADMIN_PASSWORD": service_admin_password,
            "ROLE_NAME": role_name,
            "TRUSTEE_USER_NAME": trustee_user_name,
            "TRUSTOR_USER_NAME": trustor_user_name
        }
        json_payload = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'service/%s/trust' % service_id
        response = self.send('post', url_to_send, headers=headers,
                             payload=json_payload)
        json_response = json.loads(response.content)
        if 'id' in json_response:
            return json_response['id']


