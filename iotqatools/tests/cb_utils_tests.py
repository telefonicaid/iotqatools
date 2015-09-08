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

__author__ = 'xvc'
import json

from nose.tools import eq_, ok_, assert_in
from iotqatools.cb_utils import CBUtils

cb = CBUtils(instance='127.0.0.1', verbosity=0)

print "### Test ---> Version: "
print cb.version().content
print "### Test ---> Statistics: "
print cb.statistics().content
print "### Test ---> Create a entity: "

data0 = {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]}
cb.entity_append('x222', data0)

print "### Test ---> Recover the entity1 (method1): "
entity1 = cb.entity_get('x222', 'Sala01')
eq_(200, entity1.status_code, msg="Error Code")

print "### Test ---> Recover the entity2 (method2):"
entity2 = cb.entities_get('x222', 'Sala', 'Sala01', 'false')
eq_(200, entity2.status_code, msg="Error Code")

print "### Test ---> Recover the entities wiht pattern (method3):"
entity3 = cb.entities_get('x222', 'Sala', 'Sala.*', 'true')
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

print "### Test ---> Recover missing entities: "
entityb1 = cb.entities_get('x222', 'Sala', 'S', 'false')
eq_(200, entityb1.status_code, msg="Error Code")
entityb2 = cb.entities_get('x222', 'Sal', 'Sala01', 'false')
eq_(200, entityb2.status_code, msg="Error Code")

# checking it further
jsobj_b1 = json.loads(entityb1.content)
jsobj_b2 = json.loads(entityb2.content)

eq_('404', jsobj_b1['errorCode']['code'], msg="Error Code")
eq_('No context element found', jsobj_b1['errorCode']['reasonPhrase'], msg="Error Body")

eq_('404', jsobj_b2['errorCode']['code'], msg="Error Code")
eq_('No context element found', jsobj_b2['errorCode']['reasonPhrase'], msg="Error Body")

print "### Test ---> Update the entity: "
data1 = {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala01',
         'attributes': [{'name': 'temperature', 'type': 'centigrade', 'value': '101'}]}
cb.entity_update('x222', data1)

print "### Test ---> Recover the updated entity: "
entity2 = cb.entity_get('x222', 'Sala01')
eq_(200, entity1.status_code, msg="Error Code")
assert_in('101', entity2.content)

print "### Test ---> Add Subscription: "
subs0 = dict(
    {'ent_type': 'Sala', 'ent_pattern': 'false', 'ent_id': 'Sala99', 'notify_url': 'http://localhost:5050/notify'})
sub = cb.subscription_add('x222', template_data=subs0)
eq_(200, sub.status_code, msg="Error Code")

jssub = json.loads(sub.content)
ok_(jssub['subscribeResponse']['subscriptionId'], msg="No subscription")
eq_(jssub['subscribeResponse']['duration'], 'PT5M', msg="No Duration")
print "### Test ---> subscription added:"
print "Subscription id: {}".format(jssub['subscribeResponse']['subscriptionId'])
print "Subscription duration: {}".format(jssub['subscribeResponse']['duration'])