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

import requests
import pystache

from iotqatools.templates.ac_templates import *
from iotqatools.iot_logger import get_logger


def generate_url(host, tenant, subject):
    return host + '/pap/v1/' + tenant + '/subject/' + subject


def get_subject_policies(host, tenant, subject):
    url = generate_url(host, tenant, subject)
    headers = {'content-type': 'application/xml'}
    return requests.post(url, headers=headers)


class AC(object):
    """
    Class to manage AccessControl
    Estructura de las "entities"
    fiware:<nombreDelComponente>:<Servicio>:<Subservicio>:<cualquier número de subdivisiones separadas por ':'>
    """
    BASE_PATH_MANAGE = '/pap/v1/'
    BASE_PATH_EVALUATE = '/pdp/v3/'

    log = get_logger('AccessControl', 'ERROR')

    def __init__(self, host, port='8080', protocol='http'):
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

    def create_policy(self, tenant, role, policy_name, entity, action):
        """
        Create a new policy in AC
        :param tenant:
        :param role:
        :param policy_name:
        :param entity:
        :param action:
        :return:
        """
        xml = pystache.render(template_ac_create_policy,
                              {'policy': policy_name,
                               'entity': entity,
                               'action': action})
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'subject/%s' % role
        response = self.send('post', url_to_send, headers=headers, payload=xml)
        return response

    def get_policy(self, tenant, role, policy_name):
        """
        Get a specific policy
        :param tenant:
        :param role:
        :param policy_name:
        :return:
        """
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'subject/%s/policy/%s' % (role, policy_name)
        response = self.send('get', url_to_send, headers=headers)
        return response

    def get_subject_policy(self, tenant, role):
        """
        Get all policies of a subject (Rol)
        :param tenant:
        :param role:
        :return:
        """
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'subject/%s' % role
        response = self.send('get', url_to_send, headers=headers)
        return response

    def delete_policy(self, tenant, role, policy):
        """
        Delete a specific policy
        :param tenant:
        :param role:
        :param policy:
        :return:
        """
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'subject/%s/policy/%s' % (role, policy)
        response = self.send('delete', url_to_send, headers=headers)
        return response

    def delete_subject_policies(self, tenant, role):
        """
        Delete all policies of a subject (Rol)
        :param tenant:
        :param role:
        :return:
        """
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE + 'subject/%s' % role
        response = self.send('delete', url_to_send, headers=headers)
        return response

    def delete_tenant_policies(self, tenant):
        """
        Delete all policies of a tenent
        :param tenant:
        :return:
        """
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_MANAGE
        response = self.send('delete', url_to_send, headers=headers)
        return response

    def evaluate(self, tenant, role, entity, action):
        """
        Evaluate a policy
        :param tenant:
        :param role:
        :param entity:
        :param action:
        :return:
        """
        xml = pystache.render(template_ac_evaluate,
                              {'role': role,
                               'entity': entity,
                               'action': action})
        headers = {
            'Content-type': 'application/xml',
            'Accept': 'application/xml',
            'Fiware-Service': str(tenant)
        }
        url_to_send = self.url + self.BASE_PATH_EVALUATE
        response = self.send('post', url_to_send, headers=headers, payload=xml)
        return response
