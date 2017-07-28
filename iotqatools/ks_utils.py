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

import json
import re
import requests
from iotqatools.iot_tools import PqaTools

from iotqatools.iot_logger import get_logger

log = get_logger('keystone', 'ERROR')

URL_BASE = '/v3'
URL_BASE_SCIM = '/v3/OS-SCIM'

ENDPOINTS = {
    'tokens': URL_BASE + '/auth/tokens',
    'domains': URL_BASE + '/domains',
    'roles': URL_BASE + '/roles',
    'roles_assignments': URL_BASE + '/role_assignments',
    'users': URL_BASE + '/users',
    'projects': URL_BASE + '/projects',
    'users_scim': URL_BASE_SCIM + '/Users',
    'roles_scim': URL_BASE_SCIM + '/Roles',
    'set_roles': URL_BASE + '/domains/${ID_DOM1}/users/${ID_ADM1}/roles/${ROLE_ID}',
    'set_roles_project': URL_BASE + '/projects/${ID_PROJECT}/users/${ID_ADM1}/roles/${ROLE_ID}'
}

class RequestUtils(object):
    @staticmethod
    def send(endpoint, method, headers={}, payload={}, url_parameters_list=[], query={}, verify=False):
        """
        Send a request to a specific endpoint in a specifig type of http request
        """
        if url_parameters_list != []:
            log.debug('Setting the parameters "%s" in the url "%s' % (url_parameters_list, endpoint))
            for parameter in url_parameters_list:
                endpoint = re.sub(r'\${.*?}', parameter, endpoint, 1)
        log.debug('**************************************************************************************\nSending:')
        parameters = {
            'method': method,
            'url': endpoint,
        }
        log.debug('\t*Method:\n %s' % method)
        log.debug('\t*Url:\n %s' % endpoint)
        if headers != {}:
            parameters.update({'headers': headers})
            log.debug('\t*Headers:\n %s' % headers)
        if payload != {}:
            try:
                parameters.update({'data': json.dumps(payload)})
                log.debug('\t*Payload:\n %s' % json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': ')))
            except ValueError:
                parameters.update({'data': payload})
                log.debug('\t*Payload:\n %s' % payload)
        if query != {}:
            parameters.update({'params': query})
            log.debug('\tQuery:\n %s' % query)
        if headers != {}:
            parameters.update({'verify': verify})
            log.debug('\t*Verify:\n %s' % verify)
        log.debug('End Sending\n**************************************************************************************')
        response = requests.request(**parameters)
        PqaTools.log_fullRequest(comp='ORC', response=response, params=parameters)

        return response

    @staticmethod
    def get_value_from_json_response(response, value):
        """
        Get a specific key from a json response
        """
        try:
            dict_ = json.loads(response.text)
        except ValueError:
            raise NameError('The response is not a Json, the response is: {response}'.format(response=response.text))
        if value in dict_:
            return dict_[value]
        else:
            raise NameError('The response has not the attribute "{value}. The response is: {response}"'.format(value=value, response=response))

    @staticmethod
    def get_value_from_headers_response(response, value):
        """
        Get a specific header from a response
        """
        try:
            dict_ = dict({k.lower(): v for k, v in response.headers.items()})
        except ValueError:
            raise NameError('The headers of the response are not a dict, the headers are: {header} \nThe body is: {body}'.format(header=response.headers, body=response.text))
        if value in dict_:
            return dict_[value.lower()]
        else:
            raise NameError('The response headers have not the head requested "{head}", the headers are: {headers} \nThe body is: {body}'.format(head=value, headers=response.headers, body=response.text))


class Keystone(object):
    """
    Father class with the basic operations in keystone of each type
    """

    def __init__(self, token, ip, port='5000'):
        self.url = 'http://%s:%s' % (ip, port)
        self.url_base = self.url
        self.r = RequestUtils()
        self.token = token
        self.headers = {"Content-Type": "application/json", "X-Auth-Token": self.token}
        self.payload = {}
        self.url_parameters_list = []
        self.query = {}
        self.name = 'keystone'

    def _add_object(self):
        log.debug('add object %s' % self.name)
        return self.r.send(self.url_base, 'post', self.headers, self.payload, self.url_parameters_list)

    def _list_object(self, query={}):
        if query != {}:
            for element in query.keys():
                self.query.update({element: query[element]})
        return self.r.send(self.url_base, 'get', self.headers, {}, self.url_parameters_list, self.query)

    def _details_object(self, object_):
        return self.r.send(self.url_base + '/' + object_, 'get', self.headers, {}, self.url_parameters_list, self.query)

    def _update_object(self, object_):
        return self.r.send(self.url_base + '/' + object_, 'patch', self.headers, self.payload, self.url_parameters_list,
                           self.query)

    def _delete_object(self, object_):
        return self.r.send(self.url_base + '/' + object_, 'delete', self.headers, {}, self.url_parameters_list,
                           self.query)


class Domains(Keystone):
    """
    Class to manage the keystone domains
    """
    def __init__(self, token, ip, port='5000'):
        Keystone.__init__(self, token, ip, port)
        self.name = 'domains'
        self.url_base += ENDPOINTS[self.name]

    def construct_post(self, name=None, description=None, enabled=None):
        """
        Function to build the specific post for domains
        """
        self.payload = {
            "domain": {
            }
        }
        if name is not None:
            self.payload['domain'].update({"name": name})
        if description is not None:
            self.payload['domain'].update({"description": description})
        if enabled is not None and isinstance(enabled, bool):
            self.payload['domain'].update({"enabled": enabled})

    def add(self, name=None, description=None, enabled=None):
        """
        Create a new domain
        """
        self.construct_post(name, description, enabled)
        return super(Domains, self)._add_object()

    def list(self, query={}):
        """
        List all the existing domains
        """
        return super(Domains, self)._list_object(query)

    def details(self, domain_id):
        """
        Details of a specific domain
        """
        return self._details_object(domain_id)

    def update(self, domain_id, name=None, description=None, enabled=None):
        """
        Update the an specific domain
        """
        self.construct_post(name, description, enabled)
        return self._update_object(domain_id)

    def delete(self, domain_id):
        """
        Delete the domain (and all objects that reference the domain)
        """
        return self._delete_object(domain_id)


class Projects(Keystone):
    """
    Class to manage the keystone projects
    """
    def __init__(self, token, ip, port='5000'):
        Keystone.__init__(self, token, ip, port)
        self.name = 'projects'
        self.url_base += ENDPOINTS[self.name]

    def construct_post(self, name=None, domain_id=None, description=None, enabled=None):
        """
        Function to build the specific post for projects
        """
        self.payload = {
            "project": {
            }
        }
        if name is not None:
            self.payload['project'].update({'name': name})
        if domain_id is not None:
            self.payload['project'].update({'domain_id': domain_id})
        if description is not None:
            self.payload['project'].update({'description': description})
        if enabled is not None:
            self.payload['project'].update({'enabled': enabled})

    def add(self, name=None, domain_id=None, description=None, enabled=None):
        """
        Create a new projects
        """
        self.construct_post(name, domain_id, description, enabled)
        return self._add_object()

    def list(self, domain_id):
        """
        List all the existing projects
        """
        query = {'domain_id': domain_id}
        return self._list_object(query)

    def details(self, project_id):
        """
        Details of a specific projects
        """
        return self._details_object(project_id)

    def update(self, project_id, name=None, domain_id=None, description=None, enabled=None):
        """
        Update the an specific projects
        """
        self.construct_post(name, domain_id, description, enabled)
        return self._update_object(project_id)

    def delete(self, project_id):
        """
        Delete the domain (and all objects that reference the projects)
        """
        return self._delete_object(project_id)


class Users(Keystone):
    def __init__(self, token, ip, port='5000'):
        Keystone.__init__(self, token, ip, port)
        self.name = 'users'
        self.url_base += ENDPOINTS[self.name]

    def construct_post(self, name=None, password=None, domain_id=None, description=None, enabled=None, email=None):
        """
        Function to build the specific post for users
        """
        self.payload = {
            "user": {
            }
        }
        if name is not None:
            self.payload['user'].update({'name': name})
        if domain_id is not None:
            self.payload['user'].update({'domain_id': domain_id})
        if description is not None:
            self.payload['user'].update({'description': description})
        if enabled is not None:
            self.payload['user'].update({'enabled': enabled})
        if password is not None:
            self.payload['user'].update({'password': password})
        if email is not None:
            self.payload['user'].update({'email': email})

    def add(self, name=None, password=None, domain_id=None, description=None, enabled=None, email=None):
        """
        Create a new user
        """
        self.construct_post(name, password, domain_id, description, enabled, email)
        return self._add_object()

    def list(self, query={}):
        """
        List all the existing users
        """
        return self._list_object(query)

    def details(self, id):
        """
        Details of a specific user
        """
        return self._details_object(id)

    def update(self, user_id, name=None, password=None, domain_id=None, description=None, enabled=None, email=None):
        """
        Update the an specific users
        """
        self.construct_post(name, password, domain_id, description, enabled, email)
        return self._update_object(user_id)

    def delete(self, user_id):
        """
        Delete the user
        """
        return self._delete_object(user_id)


class Roles(Keystone):
    def __init__(self, token, ip, port='5000'):
        Keystone.__init__(self, token, ip, port)
        self.name = 'roles'
        self.url_base += ENDPOINTS[self.name]

    def construct_post(self, name=None):
        """
        Function to build the specific post for roles
        """
        self.payload = {
            "role": {
            }
        }
        if name is not None:
            self.payload['role'].update({'name': name})

    def add(self, name=None):
        """
        Create a new rol
        """
        self.construct_post(name)
        return self._add_object()

    def list(self, query={}):
        """
        Query admits Name, page, per_page
        """
        return self._list_object(query)

    def assignments(self, user_id='', query={}):
        """
        Query admit user.id
        """
        query_ = {}
        if user_id != '':
            query_ = {'user.id': user_id}
        query_.update(query)
        return self.r.send(self.url + ENDPOINTS['roles_assignments'], 'get', self.headers, {}, [], query_)

    def grant_role_to_domain_user(self, user_id, domain_id, role_id):
        """
        Assign a role to an user in a domain
        """
        return self.r.send(self.url + ENDPOINTS['set_roles'], 'put', self.headers, self.payload, [domain_id, user_id,
                                                                                                  role_id])

    def grant_role_to_project_user(self, user_id, project_id, role_id):
        """
        Assign a role to an user in a project
        """
        return self.r.send(self.url + ENDPOINTS['set_roles_project'], 'put', self.headers, self.payload,
                           [project_id, user_id, role_id])


class RolesScim(Keystone):
    def __init__(self, token, ip, port='5000'):
        Keystone.__init__(self, token, ip, port)
        self.name = 'roles_scim'
        self.url_base = self.url + ENDPOINTS[self.name]
        self.query = {}

    def construct_post(self, name=None, domain_id=None):
        """
        Function to build the specific post for Roles managad by scim
        """
        self.payload = {
            "schemas": ["urn:scim:schemas:extension:keystone:1.0"],
        }
        if name is not None:
            self.payload.update({'name': name})
        if domain_id is not None:
            self.payload.update({'domain_id': domain_id})

    def add(self, name=None, domain_id=None):
        """
        Create a new rol
        """
        self.construct_post(name, domain_id)
        return self._add_object()

    def list(self, query={}):
        """
        List all the existing roles
        """
        return self._list_object(query)

    def details(self, role_id):
        """
        Details of a specific rol
        """
        return self._details_object(role_id)

    def update(self, role_id, name=None, add_domain=True):
        """
        Update the an specific rol
        """
        self.construct_post(name, add_domain)
        return self._update_object(role_id)

    def delete(self, role_id):
        """
        Delete the rol
        """
        return self._delete_object(role_id)


class UsersScim(Keystone):
    def __init__(self, token, ip, port='5000'):
        Keystone.__init__(self, token, ip, port)
        self.name = 'users_scim'
        self.url_base = self.url + ENDPOINTS[self.name]
        self.query = {}

    def construct_post(self, name=None, password=None, email=None, active=None, domain_id=None):
        """
        Function to build the specific post for Users managed by scim
        """
        self.payload = {
            "schemas": ["urn:scim:schemas:core:1.0", "urn:scim:schemas:extension:keystone:1.0"]
        }
        if name is not None:
            self.payload.update({'userName': name})
        if password is not None:
            self.payload.update({'password': password})
        if email is not None:
            self.payload.update({'emails': [{"value": email}]})
        if active is not None:
            self.payload.update({'active': active})
        if domain_id is not None:
            self.payload.update({"urn:scim:schemas:extension:keystone:1.0": {"domain_id": domain_id}})

    def add(self, name=None, password=None, email=None, active=None, domain_id=None):
        """
        Create a new user
        """
        self.construct_post(name, password, email, active, domain_id)
        return self._add_object()

    def list(self, domain_id, query={}):
        """
        List all the existing users
        """
        query.update({'domain_id': domain_id})
        return self._list_object(query)

    def details(self, user_id):
        """
        Details of a specific user
        """
        return self._details_object(user_id)

    def update(self, user_id, name=None, add_domain=True):
        """
        Update the an specific user
        """
        self.construct_post(name, add_domain)
        return self._update_object(user_id)

    def delete(self, user_id):
        """
        Delete the user
        """
        return self._delete_object(user_id)


class KeystoneCrud(object):
    """
    Class to manage any kind of keystone action
    """

    def __init__(self, username, password, domain, ip, port='5000', protocol='http', verify=False):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.url = '%s://%s:%s' % (self.protocol, self.ip, self.port)
        self.username = username
        self.password = password
        self.domain = domain
        self.r = RequestUtils()
        self.token = ''
        self.token_response = ''
        self.users = None
        self.services = None
        self.subservices = None
        self.roles = None
        self.roles_scim = None
        self.users_scim = None
        self.verify = verify

    def __check_instance(self, instance):
        """
        If there is not a token requeted, one is asked and create a keyston instance if it not exist the one given
        :param instance:
        :return:
        """
        log.debug('__check_instance - instance: %s' % instance)
        if self.token == '':
            self.get_token()
        if self.__getattribute__(instance) is None:
            attribs = {'token': self.token, 'ip': self.ip, 'port': self.port}
            if instance == 'users':
                self.__setattr__(instance, Users(**attribs))
            elif instance == 'services':
                self.__setattr__(instance, Domains(**attribs))
            elif instance == 'roles':
                self.__setattr__(instance, Roles(**attribs))
            elif instance == 'subservices':
                self.__setattr__(instance, Projects(**attribs))
            elif instance == 'roles_scim':
                self.__setattr__(instance, RolesScim(**attribs))
            elif instance == 'users_scim':
                self.__setattr__(instance, UsersScim(**attribs))
            else:
                raise NameError('The attribute %s hast no instance method in KeystoneCrud class' % instance)

    def ask_for_token(self, username=None, password=None, domain=None, project=None, trust_id=None):
        """
        Ask for a token to keystone. To get a correct token, it depends of the IoT rol.
        There are more ways to ask for a token, see the official keystone documentation
        All parameters are optional because is needed to do bad requests, but for ok request, username, password and
        domain are mandatory
        :param username: Mandatory for a rigth request
        :param password: Mandatory for a rigth request
        :param domain: Mandatory for a rigth request
        :param project: This attribute is mandatory if the user is the GlobalPlatformAdmin
        :param trust_id: Trust ID
        :return: A response object
        """
        log.debug('ask_for_token - username: %s ;; password: %s ;; domain: %s ;; project: %s' %
        (str(username), str(password), str(domain), str(project)))
        if username is None or password is None or domain is None:
            user = self.username
            passwd = self.password
            dom = self.domain
        else:
            user = username
            passwd = password
            dom = domain
        headers = {"Content-Type": "application/json"}
        payload = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "name": dom
                            },
                            "name": user,
                            "password": passwd
                        }
                    }
                }
            }
        }
        if project is None:
            payload['auth'].update({"scope": {"domain": {"name": dom}}})
        else:
            payload['auth'].update({'scope': {'project': {'name': project, "domain": {"name": dom}}}})

        if trust_id:
            # Overwrite scope
            payload['auth']['scope'] = { "OS-TRUST:trust": { "id": trust_id } }

        return self.r.send(self.url + ENDPOINTS['tokens'], 'post', headers, payload, verify=self.verify)

    def get_token(self, project=None):
        """
        Get the token and store its value and the response object in the attributes of the class
        :return: an string with the token
        """
        log.debug('get_token')
        if self.token == '':
            self.token_response = self.ask_for_token(project=project)
            self.token = self.r.get_value_from_headers_response(self.token_response, 'x-subject-token')
        return self.token

    def user_login(self, username, password, domain):
        """
        Ask for a user, not store the value in the attribute class
        :param username:
        :param password:
        :param domain:
        :return: a response object
        """
        log.debug('user_login - username: %s, password: %s, domain: %s' % (str(username), str(password), str(domain)))
        return self.ask_for_token(username, password, domain)

    def user_create(self, username, password, service_id, description=None, email=None, enabled=True):
        """
        Create a new user in a Service(Domain). The token have to own to an User with "admin" Role in the Service(Domain)
        or own to the RegionalServiceProvider
        Any of the parameters could be None. When a parameter is None, this parameter is not sent in the post. Is done to
        have de capability of raise errors.
        :param username: Username of the new User
        :param password: Password of the new User
        :param service_id: The id of the service (Domain) where the user is created
        :param description: Description of the user
        :param email: Email of the user
        :param enabled: If the user is enabled
        :return: a response object
        """
        log.debug('user_create - username: %s ;; password: %s ;; service_id: %s ;; description: %s ;; email: %s ;; enabled: %s' %
        (str(username), str(password), str(service_id), str(description), str(email), str(enabled)))
        self.__check_instance('users')
        return self.users.add(username, password, service_id, description, enabled, email)

    def user_list(self, query={}):
        """
        Get the user list. If the user is ServiceAdmin have to indicate de domain_id in the query
        :param query: html query as a dict, ex: query={'domain_id'; 'aasdfsd98978978sd7f'}
        :return: a respohnse obejct
        """
        log.debug('user_list - query: %s' % str(query))
        self.__check_instance('users')
        return self.users.list(query)

    def user_details(self, user_id):
        """
        Get the details of a user id
        :param user_id:
        :return: a response object
        """
        log.debug('user_details - user_id: %s' % str(user_id))
        self.__check_instance('users')
        return self.users.details(user_id)

    def user_delete(self, user_id):
        """
        Delete an user
        :param name:
        :return:
        """
        log.debug('user_delete - name: %s' % str(user_id))
        self.__check_instance('users')
        self.users.delete(user_id)

    def service_get_id(self, name):
        """
        Get the id of a service given the name. To get the id of a Service(Domain), the user has to have the Rol 'admin'
        in the Service(Domain)
        :param name: Name of a service
        :return:
        """
        log.debug('service_get_id - name: %s' % str(name))
        self.__check_instance('services')
        response = self.services.list({'name': name})
        try:
            services = self.r.get_value_from_json_response(response, 'domains')
        except:
            # log.error('The domain "%s" cant be get, the response is: %s' % (name, response))
            raise NameError('The domain "%s" could not be retrieved ' % name)
        if len(services) == 1:
            return services[0]['id']
        else:
            if len(services) < 1:
                raise NameError('There is not a service with the name "%s"' % name)
            elif len(services) > 1:
                raise NameError('There is more than one service with the name "%s"' % name)

    def service_create(self, name, description='', enabled=True):
        """
        Create a new domain. This operation is only allowed to a RegionalServbiceProvider
        :param name:
        :param description:
        :param enabled:
        :return:
        """
        log.debug('service_create - name: %s ;; description: %s ;; enabled: %s' % (str(name), str(description), str(enabled)))
        self.__check_instance('services')
        return self.services.add(name, description, enabled)

    def service_list(self, query={}):
        """
        List the services in the system
        :param query:
        :return: a response object
        """
        log.debug('service_list - query: %s' % str(query))
        self.__check_instance('services')
        return self.services.list(query)

    def service_delete(self, service_id):
        """
        Disable the service and delete it
        :param service_id:
        :return:
        """
        log.debug('service_delete - service_id: %s' % str(service_id))
        self.__check_instance('services')
        self.services.update(service_id, enabled=False)
        return self.services.delete(service_id)

    def rol_list(self):
        """
        List the roles
        :return:
        """
        log.debug('rol_list')
        self.__check_instance('roles')
        return self.roles.list()

    def rol_assigment_domain(self, domain_id, user_id, rol_id):
        """
        Assign a rol to an user in a domin
        :param domain_id:
        :param user_id:
        :param rol_id:
        :return:
        """
        log.debug('rol_assignmet_domain - domain_id: %s ;; user_id: %s ;; rol_id: %s' % (str(domain_id), str(user_id), str(rol_id)))
        self.__check_instance('roles')
        self.roles.grant_role_to_domain_user(user_id, domain_id, rol_id)

    def rol_assigment_project(self, project_id, user_id, rol_id):
        """
        Assign a rol to an user in a project
        :param project_id:
        :param user_id:
        :param rol_id:
        :return:
        """
        log.debug('rol_assignmet_project - project_id: %s ;; user_id: %s ;; rol_id: %s' % (str(project_id), str(user_id), str(rol_id)))
        self.__check_instance('roles')
        self.roles.grant_role_to_project_user(user_id, project_id, rol_id)

    def rol_assigments(self, user_id=''):
        """
        Get the role assigment to an user
        :param user_id:
        :return:
        """
        log.debug('rol_assigments - user_id: %s' % str(user_id))
        self.__check_instance('roles')
        return self.roles.assignments(user_id)

    def rol_create(self, name):
        """
        Create a new rol. This only can be done for a RegionalServbiceProvider
        :param name:
        :return:
        """
        log.debug('rol_create: %s' % name)
        self.__check_instance('roles')
        return self.roles.add(name)

    def rol_create_scim(self, name, service_id):
        """
        Create a rol in a domain with the scim api
        :param name:
        :param service_id:
        :return:
        """
        log.debug('rol_create_scim - name: %s ;; service_id: %s' % (str(name), str(service_id)))
        self.__check_instance('roles_scim')
        return self.roles_scim.add(name, service_id)

    def rol_list_scim(self, domain_id):
        """
        Get list roles with SCIM api
        :return:
        """
        log.debug('rol_list_scim')
        self.__check_instance('roles_scim')
        return self.roles_scim.list({'domain_id': domain_id})

    def project_create(self, name, domain_id, description, enabled):
        """
        Create a new project in a domain. This only can be done by a SergviceAdmin
        :param name:
        :param domain_id:
        :param description:
        :param enabled:
        :return:
        """
        log.debug('project_create - name: %s ;; domain_id: %s ;; description: %s ;; enabled: %s')
        self.__check_instance('subservices')
        return self.subservices.add(name, domain_id, description, enabled)

    def project_list(self, domain_id):
        """
        List the projects. Have to be a ServiceAdmin
        :return:
        """
        log.debug('project_list - domain_id: %s' % domain_id)
        self.__check_instance('subservices')
        return self.subservices.list(domain_id)


class KeystoneUtils(object):

    @staticmethod
    def get_structure(platform):
        """
        Get the structure of the platform "all passwords are the same of names"
        :param platform:
        :return:
        """
        KeystoneUtils.check_platform_config(platform)
        structure = {}
        keystonecrud = KeystoneCRud(platform['RegionalServiceAdmin']['user'], platform['RegionalServiceAdmin']['password'],
                           platform['cloud_domain']['name'], platform['address']['ip'], platform['address']['port'])
        services = json.loads(keystonecrud.service_list().text)['domains']
        service_admins = {}
        #Append each serbvice to the dict
        for service in services:
            structure.update({service['name']: dict(service)})
            structure[service['name']].update({'users': {}})
            users = json.loads(keystonecrud.user_list({'domain_id': service['id']}).text)['users']
            service_admins.update({service['name']: ''})
            #For each service, see the users of thi service
            for user in users:
                structure[service['name']]['users'].update({user['name']: dict(user)})
                #For each user, see the roles assigment in the service
                roles = json.loads(keystonecrud.rol_assigments(user['id']).text)['role_assignments']
                roles_list = []
                for rol in roles:
                    #Only if the response is scoped by domain, add it
                    if 'scope' in rol and 'domain' in rol['scope']:
                        roles_list.append(rol['role']['id'])
                if roles_list != []:
                    structure[service['name']]['users'][user['name']].update({'roles': {}})
                    roles_ = json.loads(keystonecrud.rol_list().text)['roles']
                    for rol in roles_:
                        for rol_local in roles_list:
                            if rol['id'] == rol_local:
                                if str(rol['name']).find('#') >= 0:
                                    rol_name = rol['name'][str(rol['name']).find('#')+1:]
                                else:
                                    rol_name = rol['name']
                                structure[service['name']]['users'][user['name']]['roles'].update({rol_name: dict(rol)})
                                if rol['name'] == platform['admin_rol']['name']:
                                    service_admins[service['name']] = user['name']
            if service_admins[service['name']] != '' and service['name'] != platform['GlobalServiceAdmin']['domain'] and service['name'] != platform['cloud_domain']['name']:
                da = KeystoneCrud(service_admins[service['name']],
                                  service_admins[service['name']],
                                  service['name'], platform['address']['ip'],
                                  platform['address']['port'])
                projects = json.loads(da.project_list(service['id']).text)['projects']
                structure[service['name']].update({'projects': {}})
                for project in projects:
                    structure[service['name']]['projects'].update({project['name']: dict(project)})
                    structure[service['name']]['projects'][project['name']].update({'users': {}})
                    for user in users:
                        roles = json.loads(kesytonecrud.rol_assigments(user['id']).text)['role_assignments']
                        for rol in roles:
                            if 'scope' in rol and 'project' in rol['scope']:
                                if rol['scope']['project']['id'] == project['id']:
                                    if user['name'] not in structure[service['name']]['projects'][project['name']]['users']:
                                        structure[service['name']]['projects'][project['name']]['users'].update({user['name']: dict(user)})
                                    if 'roles' not in structure[service['name']]['projects'][project['name']]['users'][user['name']]:
                                        structure[service['name']]['projects'][project['name']]['users'][user['name']].update({'roles': {}})
                                    roles_ = json.loads(keystonecrud.rol_list().text)['roles']
                                    for rol_ in roles_:
                                        if rol_['id'] == rol['role']['id']:
                                            if str(rol_['name']).find('#') >= 0:
                                                rol_name = rol_['name'][str(rol_['name']).find('#')+1:]
                                            else:
                                                rol_name = rol_['name']
                                            structure[service['name']]['projects'][project['name']]['users'][user['name']]['roles'].update({rol_name: dict(rol_)})
        return structure



    @staticmethod
    def clean_service(platform, service_to_delete):
        """
        Util to delete/clean a domain/service. It has to be made by a RegionalServiceAdmin
        :param username:
        :param password:
        :param cloud_domain:
        :return:
        """
        keystonecrud = KeystoneCrud(platform['RegionalServiceAdmin']['user'], platform['RegionalServiceAdmin']['password'],
                  platform['cloud_domain']['name'], platform['address']['ip'], platform['address']['port'])
        service_id = keystonecrud.service_get_id(service_to_delete)
        return keystonecrud.service_delete(service_id)

    @staticmethod
    def get_token(username, password, service, ip, port='5000'):
        """
        Get a token of a keystone in the ip:port. the token cuold be scoped by domain or by domain + project
        :param ip:
        :param username:
        :param password:
        :param service:
        :param subservice:
        :param port:
        :return: a response object
        """
        header = {"Content-Type": "application/json"}
        payload = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "name": service
                            },
                            "name": username,
                            "password": password
                        }
                    }
                }
            }
        }
        try:
            response = requests.post('http://%s:%s/v3/auth/tokens' % (ip, port), headers=header, data=json.dumps(payload))
            if response.status_code != 201:
                return response
            else:
                return response.headers['x-subject-token']
        except Exception as e:
            raise NameError('Therer is a problem with the connection with keystone: %s' % e.message)



    @staticmethod
    def check_platform_config(platform):
        """
        Check if the platform config is ok
        :param platform:
        :return:
        """
        try:
            if platform is {}:
                raise NameError('The platform config is empty')
            elif 'GlobalServiceAdmin' not in platform or not all(x in platform['GlobalServiceAdmin'] for x in ['user', 'password', 'roles', 'domain', 'project']):
                raise NameError('The platform needs a GlobalServiceProvider, deployed at installation time')
            elif 'RegionalServiceAdmin' not in platform or not all(x in platform['RegionalServiceAdmin'] for x in ['user', 'password']):
                raise NameError('The platform needs a RegionalServiceAdmin, deployed at installation time')
            elif 'address' not in platform or not all(x in platform['address'] for x in ['ip', 'port']):
                raise NameError('The platform needs an address where the platform is deployed')
            elif 'pep' not in platform or not all(x in platform['pep'] for x in ['user', 'password', 'mail', 'roles']):
                # TODO: Change the print for a log warningt
                log.warning('WARNING: The platform needs a pep user to use the portal_user actions')
            elif 'cloud_domain' not in platform or 'name' not in platform['cloud_domain']:
                raise NameError('the platform needs the cloud admin name, configured at installation time')
            elif 'admin_rol' not in platform or 'name' not in platform['admin_rol']:
                raise NameError('The platform needs an admin rol, configured at installation time')
            else:
                return True
        except Exception as e:
            print "This is an example of platform config attribute"
            print """
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
            """
            raise

    @staticmethod
    def check_environment_config(environment):
        """
        Check the mandatory attributes of the environment configuration

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
                                    'name': 'coral',
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
        """
        assert 'domains' in environment, 'The domains has to be in the environment dict as a list of domains'
        for domain in environment['domains']:
            assert 'name' in domain, 'There is a domain without name, this parameter is mandatory in each domain'
            if 'users' in domain:
                assert 'domain_admin' in domain, 'There have to be domain_admin attribute to define new users'
                for user in domain['users']:
                    assert all(x in user for x in ['name', 'password']), 'If the domain has users, is mandatory a name and password to create it'
                    if 'roles' in user:
                        for rol in user['roles']:
                            assert 'name' in rol, 'To create a new rol is mandatory to set a name'
                    if 'projects' in user:
                        for project in user['projects']:
                            assert 'name' in project, 'To create a new project is mandatory to set a name'
                            if 'roles' in project:
                                for rol_project in project['roles']:
                                    assert 'name' in rol_project, 'To create or assign a rol to an user in a project is mandatory to set a name'
        return True

    @staticmethod
    def prepare_environment(platform={}, environment={}):
        """
        Provision the given structure (environament) in a keystone (platform)

        Example
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
                                    'name': 'coral',
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
        :return:
        """
        KeystoneUtils.check_platform_config(platform)
        KeystoneUtils.check_environment_config(environment)
        rsp = KeystoneCrud(platform['RegionalServiceAdmin']['user'],
                  platform['RegionalServiceAdmin']['password'],
                  platform['cloud_domain']['name'],
                  platform['address']['ip'],
                  platform['address']['port'])
        roles_list = json.loads(rsp.rol_list().text)['roles']
        rol_admin_id = ''
        for rol in roles_list:
            if rol['name'] == platform['admin_rol']['name']:
                rol_admin_id = rol['id']
                break
        assert rol_admin_id != '', 'The rol indicated as admin_rol is not in the system'
        for domain in environment['domains']:
            if 'description' in domain:
                resp = rsp.service_create(domain['name'], domain['description'], True).text
                domain_id = json.loads(resp)['domain']['id']
            else:
                resp = rsp.service_create(domain['name'], enabled=True).text
                domain_id = json.loads(resp)['domain']['id']
            if 'domain_admin' in domain and all(x in domain['domain_admin'] for x in ['username', 'password']):
                user_id = json.loads(rsp.user_create(domain['domain_admin']['username'], domain['domain_admin']['password'],
                                                     domain_id).text)['user']['id']
                rsp.rol_assigment_domain(domain_id, user_id, rol_admin_id)
                da = KeystoneCrud(domain['domain_admin']['username'],
                         domain['domain_admin']['password'],
                         domain['name'], platform['address']['ip'],
                         platform['address']['port'])
                if 'users' in domain:
                    for user in domain['users']:
                        if 'description' in user:
                            user_id = json.loads(da.user_create(user['name'], user['password'], domain_id,
                                                            user['description']).text)['user']['id']
                        else:
                            user_id = json.loads(da.user_create(user['name'], user['password'], domain_id)
                                                 .text)['user']['id']
                        if 'roles' in user:
                            roles_list_scim = json.loads(da.rol_list_scim(domain_id).text)['Resources']
                            for rol in user['roles']:
                                exist = False
                                for rol_in_list in roles_list_scim:
                                    if rol['name'] == rol_in_list['name']:
                                        exist = True
                                        rol_id = rol_in_list['id']
                                        break
                                if not exist:
                                    rol_id = json.loads(rsp.rol_create_scim(rol['name'], domain_id).text)['id']
                                da.rol_assigment_domain(domain_id, user_id, rol_id)
                        if 'projects' in user:
                            for project in user['projects']:
                                exist = False
                                project_list = json.loads(da.project_list(domain_id).text)['projects']
                                for project_existent in project_list:
                                    if project['name'] == project_existent['name']:
                                        exist = True
                                        break
                                if not exist:
                                    if 'description' in project:
                                        project_id = json.loads(da.project_create(project['name'],
                                                                                  domain_id,
                                                                                  project['description'], True).text)['project']['id']
                                    else:
                                        project_id = json.loads(da.project_create(project['name'],
                                                                                  domain_id,
                                                                                  enabled=True).text)['project']['id']
                                if 'roles' in project:
                                    roles_list_scim = json.loads(da.rol_list_scim(domain_id).text)['Resources']
                                    for rol in project['roles']:
                                        exist = False
                                        for rol_in_list in roles_list_scim:
                                            if rol['name'] == rol_in_list['name']:
                                                exist = True
                                                rol_id = rol_in_list['id']
                                                break
                                        if not exist:
                                            rol_id = json.loads(rsp.rol_create_scim(rol['name'], domain_id).text)['id']
                                        da.rol_assigment_project(project_id, user_id, rol_id)
