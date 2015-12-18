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

__author__ = 'jmab20'
import json

from nose.tools import eq_, ok_, assert_in
from iotqatools.cb_utils import CBUtils
import unittest
import mock

last_updateContext =""

class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = {}
            self.content = str(json_data)

        def json(self):
            return self.json_data


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):

    version = """ <orion>
                    <version>0.24.0</version>
                    <uptime>0 d, 3 h, 53 m, 28 s</uptime>
                    <git_hash>ed11a3307c7050857ef398ee3e4cd04042a0cc01</git_hash>
                    <compile_time>Mon Sep 14 17:52:44 CEST 2015</compile_time>
                    <compiled_by>fermin</compiled_by>
                    <compiled_in>centollo</compiled_in>
                  </orion>"""

    statistics = """<orion>
                      <xmlRequests>10</xmlRequests>
                      <jsonRequests>25</jsonRequests>
                      <queries>6</queries>
                      <updates>4</updates>
                      <subscriptions>11</subscriptions>
                      <versionRequests>9</versionRequests>
                      <statisticsRequests>3</statisticsRequests>
                      <invalidRequests>2</invalidRequests>
                      <subCacheEntries>10</subCacheEntries>
                      <subCacheLookups>3</subCacheLookups>
                      <uptime_in_secs>15396</uptime_in_secs>
                      <measuring_interval_in_secs>15396</measuring_interval_in_secs>
                    </orion>"""

    subscribe = """ {
                      "subscribeResponse" : {
                        "subscriptionId" : "5673c7fd9ddf69cafcf23000",
                        "duration" : "PT5M"
                      }
                    }"""

    global last_updateContext
    if kwargs["url"] == 'http://mock.cb.com:1026/v1/updateContext':
        jsobj_1 = json.loads(kwargs["data"])
        last_updateContext = jsobj_1['contextElements'][0]
        return MockResponse("", 201)
    elif kwargs["url"] == 'http://mock.cb.com:1026/v1/queryContext':
        res1 = { }
        res1["contextElement"] = last_updateContext
        response = {"contextResponses" : [] }
        response["contextResponses"].append(res1)
        return MockResponse(json.dumps(response), 200)
    elif kwargs["url"] == 'http://mock.cb.com:1026/v1/contextEntities/Sala01':
        response = { }
        response["contextElement"] = last_updateContext
        return MockResponse(json.dumps(response), 200)
    elif kwargs["url"] == 'http://mock.cb.com:1026/version':
        return MockResponse(version, 200)
    elif kwargs["url"] == 'http://mock.cb.com:1026/statistics':
        return MockResponse(statistics, 200)
    elif kwargs["url"] == 'http://mock.cb.com:1026/v1/subscribeContext':
        return MockResponse(subscribe, 200)
    elif kwargs["method"] == "get":
        response = { }
        response["contextElement"] = last_updateContext
        return MockResponse(json.dumps(response), 200)

    return MockResponse("not found " + kwargs["url"], 404)

def mocked_requests_404(*args, **kwargs):

    notfound = """{"errorCode" : {
                    "code" : "404",
                    "reasonPhrase" : "No context element found"
                    }
                  }"""

    return MockResponse(notfound, 200)

class CBUtilsTest(unittest.TestCase):

   def setUp(self):
      self.cb = CBUtils(instance='mock.cb.com', port="1026", verbosity=0)
  #    self.cb = CBUtils(instance='195.235.93.78', port="10026", path_context="/cb/v1/contextEntities", path_query="/cb/v1/queryContext",
  #                      path_statistics="/cb/statistics",
  #                      path_subscription="/cb/v1/subscribeContext",
  #                      path_update="/cb/v1/updateContext",
  #                      path_version="/cb/version",
  #                      verbosity=0)

   @mock.patch('requests.request', side_effect=mocked_requests_get)
   def test_version(self, mock_requests):
       version = self.cb.version()
       print "### Test ---> Version: " + version.content
       eq_(200, version.status_code, msg="version to CB does not return 200")
       assert_in("orion", version.content, msg="bad data returned to query version to CB")
       assert_in("version", version.content, msg="bad data returned to query version to CB")

   @mock.patch('requests.request', side_effect=mocked_requests_get)
   def test_statistics(self, mock_requests):
       print "### Test ---> Statistics: "
       print self.cb.statistics().content

   @mock.patch('requests.request', side_effect=mocked_requests_get)
   def test_create_entity(self, mock_requests):
       print "### Test ---> Create a entity: "
       data0 = {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]}
       self.cb.entity_append('x222', data0)

       print "### Test ---> Recover the entity1 (method1): "
       entity1 = self.cb.entity_get('x222', 'Sala01')
       eq_(200, entity1.status_code, msg="Error Code")

       print "### Test ---> Recover the entity2 (method2):"
       entity2 = self.cb.entities_get('x222', 'Sala', 'Sala01', 'false')
       eq_(200, entity2.status_code, msg="Error Code")

       print "### Test ---> Recover the entities wiht pattern (method3):"
       entity3 = self.cb.entities_get('x222', 'Sala', 'Sala.*', 'true')
       eq_(200, entity2.status_code, msg="Error Code")

       print "### Test ---> Compare all the entities recovered: "
       jsobj_1 = json.loads(entity1.content)
       jsobj_2 = json.loads(entity2.content)
       jsobj_3 = json.loads(entity3.content)

       # Validations
       eq_('Sala', jsobj_1['contextElement']['type'], msg="DATA ERROR 1 {}".format(jsobj_1['contextElement']['type']))
       eq_('Sala01', jsobj_1['contextElement']['id'], msg="DATA ERROR 2 {}".format(jsobj_1['contextElement']['id']))
       eq_('99', jsobj_1['contextElement']['attributes'][0]['value'],
            msg="DATA ERROR 3 {}".format(jsobj_1['contextElement']['attributes'][0]['value']))
       eq_('temperature', jsobj_1['contextElement']['attributes'][0]['name'],
            msg="DATA ERROR 4 {}".format(jsobj_1['contextElement']['attributes'][0]['name']))
       eq_(jsobj_1['contextElement'],
            jsobj_2['contextResponses'][0]['contextElement'],
            msg='## Not equals!\n Received1: {} \n Received2: {}'.format(
                jsobj_1['contextElement'],
                jsobj_2['contextResponses'][0]['contextElement']))

       eq_(jsobj_3['contextResponses'][0]['contextElement'],
            jsobj_2['contextResponses'][0]['contextElement'],
            msg='## Not equals!\n Received5: {} \n Received2: {}'.format(
                jsobj_3['contextResponses'][0]['contextElement'],
                jsobj_2['contextResponses'][0]['contextElement']))

   @mock.patch('requests.request', side_effect=mocked_requests_404)
   def test_missing_entities(self, mock_requests):
        print "### Test ---> Recover missing entities: "
        entityb1 = self.cb.entities_get('x222', 'Sala', 'S', 'false')
        eq_(200, entityb1.status_code, msg="Error Code")
        entityb2 = self.cb.entities_get('x222', 'Sal', 'Sala01', 'false')
        eq_(200, entityb2.status_code, msg="Error Code")

        # checking it further
        jsobj_b1 = json.loads(entityb1.content)
        jsobj_b2 = json.loads(entityb2.content)

        eq_('404', jsobj_b1['errorCode']['code'], msg="Error Code")
        eq_('No context element found', jsobj_b1['errorCode']['reasonPhrase'], msg="Error Body")

        eq_('404', jsobj_b2['errorCode']['code'], msg="Error Code")
        eq_('No context element found', jsobj_b2['errorCode']['reasonPhrase'], msg="Error Body")

   @mock.patch('requests.request', side_effect=mocked_requests_get)
   def test_update_entity(self, mock_requests):
        print "### Test ---> Update the entity: "
        data0 = {'ent_type': 'Salass', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]}
        self.cb.entity_append('x222', data0)

        print "### Test ---> Recover the entity1 (method1): "
        entity1 = self.cb.entity_get('x222', 'Sala01')

        data1 = {'ent_type': 'Salass', 'ent_pattern': 'false', 'ent_id': 'Sala01',
                 'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '101'}]}
        self.cb.entity_update('x222', data1)

        print "### Test ---> Recover the updated entity: "
        entity2 = self.cb.entity_get('x222', 'Sala01')
        eq_(200, entity1.status_code, msg="Error Code")
        assert_in('101', entity2.content)

   @mock.patch('requests.request', side_effect=mocked_requests_get)
   def test_subscription(self, mock_requests):
        print "### Test ---> Add Subscription: "
        data0 = {'ent_type': 'Salass', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]}
        self.cb.entity_append('x222', data0)

        subs0 = dict(
            {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala99', 'notify_url': 'http://localhost:5050/notify'})
        sub = self.cb.subscription_add('x222', template_data=subs0)
        eq_(200, sub.status_code, msg="Error Code")

        jssub = json.loads(sub.content)
        ok_(jssub['subscribeResponse']['subscriptionId'], msg="No subscription")
        eq_(jssub['subscribeResponse']['duration'], 'PT5M', msg="No Duration")
        print "### Test ---> subscription added:"
        print "Subscription id: {}".format(jssub['subscribeResponse']['subscriptionId'])
        print "Subscription duration: {}".format(jssub['subscribeResponse']['duration'])


if __name__ == '__main__':
    unittest.main()


