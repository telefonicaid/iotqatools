# -*- coding: utf-8 -*-
"""
Copyright 2015 Telefonica Investigación y Desarrollo, S.A.U

This file is part of telefonica-iot-qa-tools

orchestrator is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

orchestrator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with orchestrator.
If not, seehttp://www.gnu.org/licenses/.

For those usages not covered by the GNU Affero General Public License
please contact with::[iot_support@tid.es]
"""

__author__ = 'avega'

import json
import requests

from iotqatools.iot_tools import get_logger


class Orchestrator(object):
    """
    Class to manage Orchestrator
    """
    BASE_PATH_MANAGE = '/v1.0/'

    log = get_logger('Orchestrator', 'ERROR')

    def __init__(self, host='127.0.0.1', port='8084', protocol='http'):
        self.url = '%s://%s:%s' % (protocol, host, port)

    def send(self, method, url, headers=None, payload=None, query=None):
        """
        Funtion to send requests printing data to send by log
        :param method: get, post, delete, patch, update...
        :param url:
        :param headers:
        :param payload:
        :param query:
        :return: response object
        """
        self.log.debug('Request: -->')
        self.log.debug('Method: %s' % method)
        self.log.debug('Url: %s' % url)
        self.log.debug('headers: %s' % headers)
        self.log.debug('query: %s' % query)
        self.log.debug('payload: %s' % payload)
        self.log.debug('--------------')
        request_parms = {}
        if headers is not None:
            request_parms.update({'headers': headers})
        if payload is not None:
            request_parms.update({'data': payload})
        if query is not None:
            request_parms.update({'params': query})
        response = requests.request(method, url, **request_parms)
        self.log.debug('Response: -->')
        self.log.debug('Return code: %s' % response.status_code)
        self.log.debug('Resturn headers: %s' % response.headers)
        self.log.debug('Return data: %s' % response.text)
        return response

    def _get_service_id(self,
                        service_name,
                        admin_domain_user='cloud_admin',
                        admin_domain_password='password'):

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
        # TODO: get service_name id
        json_response = json.loads(response.content)
        for domain in json_response['domains']:
            if domain['name'] == service_name:
                return domain['id']
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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
                                service_id,
                                service_admin_user,
                                service_admin_password,
                                new_service_user_name,
                                new_service_user_password,
                                new_service_user_email,
                                new_service_user_description):
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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
                                 service_id,
                                 service_admin_user,
                                 service_admin_password,
                                 role_name,
                                 service_user_name):
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
            service_id = self._get_service_id(service_name)
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
                                    service_id,
                                    subservice_name,
                                    service_admin_user,
                                    service_admin_password,
                                    role_name,
                                    service_user_name,
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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
            service_id = self._get_service_id(service_name)
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


if __name__ == '__main__':
    orc = Orchestrator('localhost', '8084', 'http')
    res = orc.create_new_service('admin_domain',
                                 'cloud_admin',
                                 'password',
                                 'foocity',
                                 'myfoocity',
                                 'adm1',
                                 'password',
                                 'adm@iot.tid.com')
    print res
    try:
        service_id = json.loads(res.content)['id']
    except Exception:
        res = orc.remove_service('foocity',
                                 'cloud_admin',
                                 'password')
        exit(0)

    res = orc._get_service_id('foocity')
    print res

    res = orc.create_new_subservice('foocity',
                                    service_id,
                                    'adm1',
                                    'password',
                                    'jardines',
                                    'jardines del pueblo')
    print res
    res = orc.create_new_service_user('foocity',
                                      service_id,
                                      'adm1',
                                      'password',
                                      'bart',
                                      'password',
                                      'bat@iot.tid.es',
                                      'Mr. Bart'
                                      )
    print res
    user_id = json.loads(res.content)['id']
    res = orc.create_new_service_role('foocity',
                                      service_id,
                                      'adm1',
                                      'password',
                                      'Boss'
                                      )
    role_id = json.loads(res.content)['id']
    print res
    res = orc.assign_role_service_user('foocity',
                                       service_id,
                                       'adm1',
                                       'password',
                                       'Boss',
                                       'bart')
    print res
    res = orc.unassign_role_service_user('foocity',
                                         service_id,
                                         'adm1',
                                         'password',
                                         'Boss',
                                         'bart')
    print res
    res = orc.remove_service_role('foocity',
                                  service_id,
                                  'adm1',
                                  'password',
                                  'Boss',
                                  role_id
                                  )
    print res
    res = orc.assign_role_subservice_user('foocity',
                                          service_id,
                                          'jardines',
                                          'adm1',
                                          'password',
                                          'SubServiceCustomer',
                                          'bart')
    print res
    trust_id = orc.create_trust_token('foocity',
                                      service_id,
                                      'jardines',
                                      'adm1',
                                      'password',
                                      'SubServiceAdmin',
                                      'bart',
                                      'adm1',
                                      )
    print trust_id
    res = orc.unassign_role_subservice_user('foocity',
                                            service_id,
                                            'jardines',
                                            'adm1',
                                            'password',
                                            'SubServiceCustomer',
                                            'bart')
    print res
    res = orc.remove_service_user('foocity',
                                  service_id,
                                  'adm1',
                                  'password',
                                  'bart',
                                  user_id
                                  )
    print res
    res = orc.remove_subservice('foocity',
                                service_id,
                                'adm1',
                                'password',
                                'jardines')
    print res
    res = orc.remove_service('foocity',
                             'cloud_admin',
                             'password')
    print res
