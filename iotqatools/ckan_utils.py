# -*- coding: utf-8 -*-
"""
(c) Copyright 2014 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
"""

import requests
import json

from iotqatools.iot_logger import get_logger
from requests.exceptions import RequestException
from iotqatools.iot_tools import PqaTools

DEFAULT_ENDPOINT = 'localhost'
DEFAULT_APIKEY = '7b321ca7-2193-4adf-8039-d550428620fe'
DEFAULT_PATH = '/api/3/action'
DEFAULT_URL = 'http://foo.es/resource'
DEFAULT_PROTOCOL = 'http'
DEFAULT_PORT = '8443'


class CKANUtils:
    def __init__(self, instance=DEFAULT_ENDPOINT,
                 apikey=DEFAULT_APIKEY,
                 path=DEFAULT_PATH,
                 port=DEFAULT_PORT,
                 url=DEFAULT_URL,
                 protocol=DEFAULT_PROTOCOL,
                 verbosity='DEBUG',
                 default_headers={"Accept": "application/json", 'content-type': 'application/json'}):
        """
        Method for initialization of CKAN. Basically you can set the endpoint and the apikey of the user you are going
        to use by initializing the class (e.g. ckan = CkanUtils(instance='http://81.45.57.227:8443',
        apikey='7b321ca7-2193-4adf-8039-d550428620fe')
        :param instance: endpoint of the ckan instance (e.g. 192.168.21.194)
        :param apikey: unique identifier of the ckan user
        :param path: ckan path
        :param port: ckan listen port
        :param url: url to include in the resources creation
        :param protocol: ckan protocol (e.g. http, https)
        :param verbosity: verbosity level ('CRITICAL','ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')
        :param default_headers: default headers for every requests to be sent to ckan
        """
        # initialize logger
        self.log = get_logger('ckan_utils', verbosity)

        self.instance = instance
        self.apikey = apikey
        self.path = path
        self.protocol = protocol
        self.port = port
        self.url = url
        self.verbosity = verbosity
        self.default_headers = default_headers

    def compose_url(self, protocol, endpoint, port, path, action):
        """
        Function to compose the url of the different actions
        :param protocol: the protocol set by the instance of the class (e.g. https)
        :param port: ckan listen port
        :param endpoint: endpoint of the instance of CKAN. e.g. 'http://81.45.57.227:8443'
        :param path: by default '/api/3/action'
        :param action: the action to be executed
        :return: the url (string) e.g. 'http://81.45.57.227:8443//api/3/action/organization_create'
        """
        url = protocol + '://' + endpoint + ':' + port + path + action
        return url

    def __send_request(self, method, url, headers=None, payload=None, verify=None, query=None):
        """
        Send a request to a specific url in a specific type of http request
        :param method: http method (get | post | put | delete)
        :param url: url of the requests
        :param headers: headers of the request
        :param payload: payload of the request
        :param verify: if the requests has SSL verification on client (True | False)
        :param query: params of the request
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
            PqaTools.log_requestAndResponse(url=url, headers=headers, data=payload, comp='CKAN')
            assert False, 'ERROR: [NETWORK ERROR] {}'.format(e)

        # Log data
        PqaTools.log_fullRequest(comp='CKAN', response=response, params=parameters)
        return response

    def create_organization(self, organization_name, verify_ssl=False):
        """
        Function to create organizations
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param organization_name: the name of the organization you want to create
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/organization_create')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        payload = {'name': organization_name}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def delete_organization(self, organization_name, verify_ssl=False):
        """
        Function to delete organizations
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param organization_name: the name of the organization you want to delete
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/organization_delete')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        organization_id = self.get_organization_id(organization_name)
        payload = {'id': organization_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def purge_organization(self, organization_name, verify_ssl=False):
        """
        Function to purge organizations
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param organization_name: the name of the organization you want to delete
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/organization_purge')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        organization_id = self.get_organization_id(organization_name)
        payload = {'id': organization_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def purge_trash(self, organization_name, verify_ssl=False):
        """
        Function to purge data
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/ckan-admin/trash')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        payload = 'purge-packages=purge'
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def get_organization_id(self, organization_name, verify_ssl=False):
        """
        Function to retrieve the id of an organization given the name
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param organization_name: the name of the organization we want to retrieve the id
        :return: id of the organization (string)
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/organization_show')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        params = {"id": organization_name}
        response = self.__send_request('get', url, headers=headers, verify=verify_ssl, query=params)
        organization_id = str(response.json()['result']['id'])
        return organization_id

    def create_package(self, package_name, organization_name, verify_ssl=False):
        """
        Function to create a package in an organization
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param package_name: name of the package we are going to create
        :param organization_name: name of an existing organization the package is going to belong
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/package_create')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        payload = {"name": package_name,
                   "owner_org": organization_name}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def get_package_id(self, package_name, verify_ssl=False):
        """
        Function to retrieve the id of a package given the name
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param package_name: name of the package we want to know the id
        :return: id of the package (string)
        """
        response = self.get_package(package_name, verify_ssl=verify_ssl)
        package_id = str(response.json()['result']['id'])
        return package_id

    def delete_package(self, package_name, verify_ssl=False):
        """
        Function to delete a package given the name
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param package_name: the name of the package we want to delete
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/package_delete')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        package_id = self.get_package_id(package_name)
        payload = {'id': package_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def purge_package(self, package_name, verify_ssl=False):
        """
        Function to delete a package given the name
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param package_name: the name of the package we want to delete
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/package_purge')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        package_id = self.get_package_id(package_name)
        payload = {'id': package_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def create_resource(self, resource_name, package_name, resource_url=DEFAULT_URL, verify_ssl=False):
        """
        Function to create a resource in a package
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: name of the resource we want to create
        :param package_name: name of the existing package the resource is going to belong
        :param resource_url: url of the resource we are going to create
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/resource_create')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        package_id = self.get_package_id(package_name)
        payload = {
            "name": resource_name,
            "url": resource_url,
            "package_id": package_id
        }
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def create_resource_with_id(self, resource_name, package_id, resource_url=DEFAULT_URL, verify_ssl=False):
        """
        Function to create a resource in a package
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: name of the resource we want to create
        :param package_id: id of the existing package the resource is going to belong
        :param resource_url: url of the resource we are going to create
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/resource_create')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        payload = {
            "name": resource_name,
            "url": resource_url,
            "package_id": package_id
        }
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def get_resource_id(self, resource_name, package_name, verify_ssl=False):
        """
        Function to retrieve the id of a resource given the name of the resource and the name of package
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: name of the resource we want to know the id
        :param package_name: name of the package the resource belongs
        :return: id of the resource (string)
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/package_show')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        params = {"id": package_name}
        try:
            response = self.__send_request('get', url, headers=headers, verify=verify_ssl, query=params)
            for resources in response.json()['result']['resources']:
                if resources['name'] == resource_name:
                    resource_id = resources['id']
                    return resource_id
        except Exception, e:
            raise Exception("\n-- ERROR -- get_resource_id \n{}".format(e))

    def delete_resource(self, resource_name, package_name, verify_ssl=False):
        """
        Function to delete a resource given a resource name package name
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: name of the resource we want to delete
        :param package_name: name of the package where the resource belongs
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/resource_delete')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        resource_id = self.get_resource_id(resource_name, package_name)
        payload = {'id': resource_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def purge_resource(self, resource_name, package_name, verify_ssl=False):
        """
        Function to delete a resource given a resource name package name
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: name of the resource we want to delete
        :param package_name: name of the package where the resource belongs
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/resource_purge')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        resource_id = self.get_resource_id(resource_name, package_name)
        payload = {'id': resource_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def get_last_value_from_resource(self, resource_name, package_name, verify_ssl=False):
        """
        Function to retrieve the last value of a given resource
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: the name of the resource we want to know the last value
        :param package_name: the name of the package where the resource belongs
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/datastore_search_sql')
        resource_id = self.get_resource_id(resource_name, package_name)
        sql = 'SELECT * from "' + resource_id + '" ORDER BY _id DESC  LIMIT 1 '
        payload = ''
        params = 'sql=' + sql
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        # Send the request with the required parameters
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl, query=params)
        return response

    def create_datastore(self, resource_name, package_name, fields=[], verify_ssl=False):
        """
        Function to create datastore of a given resource
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :param resource_name: name of the resource we are going to create the datastore
        :param package_name: name of the package the resource belongs
        :param fields: list with the name of the attributes e.g. ['temperature','pressure']
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/datastore_create')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        resource_id = self.get_resource_id(resource_name, package_name)
        payload = self.__create_datastore_structure(resource_id, fields)
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def __create_datastore_structure(self, resource_id, fields=[]):
        datastore_structure = {}
        list_fields = []
        recvtime = {'id': 'recvTime', 'type': 'timestamp'}
        timeinstant = {'id': 'TimeInstant', 'type': 'timestamp'}
        list_fields.append(recvtime)
        list_fields.append(timeinstant)
        for field in fields:
            list_fields.append({'id': field, 'type': 'json'})
        datastore_structure['resource_id'] = str(resource_id)
        datastore_structure['fields'] = fields
        datastore_structure['force'] = "true"
        return datastore_structure

    def get_resource(self, resource_name, package_name, verify_ssl=False):
        """
        Function that returns the resource, given the resource name and the package
        :param resource_name: name of the resource
        :param package_name: name of the package
        :param verify_ssl: if the requests has SSL verification on client (True | False)
        :return: response object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/resource_show')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        resource_id = self.get_resource_id(resource_name, package_name)
        payload = {"id": resource_id}
        response = self.__send_request('post', url, headers=headers, payload=payload, verify=verify_ssl)
        return response

    def get_package(self, package_name, verify_ssl=False):
        """
        Function that returns the package, given the package name
        :param package_name: name of the package
        :param verify_ssl: Function that returns the resource given the resource name and the package
        :return: returns object
        """
        url = self.compose_url(self.protocol, self.instance, self.port, self.path, '/package_show')
        headers = {'Authorization': self.apikey, 'Content-Type': 'application/json'}
        params = {"id": package_name}
        response = self.__send_request('get', url, headers=headers, verify=verify_ssl, query=params)
        return response

