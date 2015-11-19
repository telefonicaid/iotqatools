

import json
import requests
import ast
from iotqatools.iot_logger import get_logger

from behave import *
from nose.tools import assert_true
from iotqatools.iot_tools import PqaTools

__logger__ = get_logger("CKAN_utils", 'DEBUG', True)

class CkanUtils(object):

    @staticmethod
    def get_last_value_from_resource(context, endpoint, apikey, resourceid):
        verify_ssl = ast.literal_eval(context.config['components']['CKAN']['verifyssl'])
        try:
            context.config['components']['CKAN']['response'] = context.o['CKAN'].get_last_value_from_resource(context,
                                                                                                              context.remember['resource'], 
                                                                                                              context.remember['package'], 
                                                                                                              verify_ssl = verify_ssl)

            result = json.loads(context.config['components']['CKAN']['response'].content)['result']

        except requests.exceptions.RequestException as e:
            __logger__.info("Network error: " + e)
            assert_true(False, msg="[NETWORK ERROR]")

        return result
    
    @staticmethod
    def ckanCreateOrg(context, comp, service, secure=False):
        assert_true(service = service.lower())
        data = PqaTools.pattern_recall("CKAN", 'create_package')
        package = json.loads(data)['data']
        verify_ssl= ast.literal_eval(context.config['components'][comp]['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o[comp].create_organization(service, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config[comp]['response'] = 'ERROR'
            __logger__.info('[ERROR] '+ e)
            assert_true(False, msg='[NETWORK ERROR]')

            # Show info in logs
            # PqaTools.log_result(url=url, headers=headers, data=data, comp=comp)
            # TODO: show log info

    @staticmethod
    def ckanCreatePkg(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        data = PqaTools.pattern_recall('CKAN', 'create_package')
        package = json.loads(data)['name']
        verify_ssl = ast.literal_eval(context.config['components'][comp]['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o[comp].create_package(package, service, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')

            # Show info in logs
            # PqaTools.log_result(url=url, headers=headers, data=data,comp=comp)
            # TODO: Show info in logs

    @staticmethod
    def ckanCreateRsc(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        data = PqaTools.pattern_recall('CKAN', 'create_resource')
        resource_name = json.loads(data)['name']
        resource_url = json.loads(data)['url']
        package_id = json.loads(data)['package_id']
        verify_ssl = ast.literal_eval(context.config['components'][comp]['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o[comp].create_resource(resource_name, package_id,
                                                                      resource_url=resource_url,
                                                                      verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')

            # Show info in logs
            # PqaTools.log_result(url=url, headers=headers, data=data,comp=comp)
            # TODO: Show info in logs

    @staticmethod
    def ckanGetRsc(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        data = PqaTools.pattern_recall('CKAN', 'show_package')
        package_name = json.loads(data)['id']
        # Send the request with the required parameters
        verify_ssl = ast.literal_eval(context.config['components'][comp]['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o[comp].get_package(package_name, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')

        # Show info in logs
        __logger__.info(" > RESPONSE: {}".format(context.config['components'][comp]['response']))
        result = json.loads(context.config['components'][comp]['response'].content)['result']

        # print result["resources"][0]["id"]
        if context.config['components'][comp]['response'].status_code == 200:
            PqaTools.remember('resource-id', result['resources'][0]['id'])

    @staticmethod
    def ckanGetPkg(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        data = PqaTools.pattern_recall('CKAN', 'show_package')
        package_name = json.loads(data)['id']
        verify_ssl = ast.literal_eval(context.config['components'][comp]['verifyssl'])
        # Send the request with the required parameters
        # verifySSL = False
        try:
            context.config['components'][comp]['response'] = context.o[comp].get_package(package_name, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')

            # Show info in logs
            # if world.vm:
            # PqaTools.log_result(url=url, headers=headers, data=data,comp=comp)
            # TODO: Show info in logs

    @staticmethod
    def ckanCreateDs(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        data = PqaTools.pattern_recall('CKAN', 'create_datastore')
        fields = json.loads(data)['fields']
        # verifySSL = False
        verify_ssl = ast.literal_eval(context.config['components'][comp]['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o[comp].create_datastore(context.remember['resource'], context.remember['package'],
                                                                       fields, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')

            # Show info in logs
            # PqaTools.log_result(url=url, headers=headers, data=data,comp=comp)
            # TODO: Show info in logs

    @staticmethod
    def ckanCreateDs2(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        data = PqaTools.pattern_recall('CKAN', 'create_datastore2')
        fields = json.loads(data)['fields']
        # verifySSL = False
        verify_ssl = ast.literal_eval(context.config['components'][comp]['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o[comp].create_datastore(context.remember['resource'], context.remember['package'],
                                                                       fields, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')



    @staticmethod
    def ckanDeleteOrg(context, comp, service, secure=False):
        # collect all the input data and mixed it with the template to send
        assert_true(service == service.lower())
        # verifySSL = False
        verify_ssl = ast.literal_eval(context.config['components']['CKAN']['verifyssl'])
        try:
            context.config['components'][comp]['response'] = context.o['CKAN'].delete_organization(service, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException, e:
            context.config['components'][comp]['response'] = 'ERROR'
            __logger__.info("Network error: " + e)
            assert_true(False, msg='[NETWORK ERROR]')
                                    
