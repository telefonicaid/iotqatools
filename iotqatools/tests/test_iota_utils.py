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

__author__ = 'jmab20'
import json
from iotqatools.iot_tools import PqaTools

from nose.tools import eq_, ok_, assert_in
from iotqatools.iota_utils import Rest_Utils_IoTA
import unittest
try:
    from unittest import mock
except ImportError:  # python2
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

    version = """Welcome to IoTAgents  identifier:IoTPlatform:8080  1.3.1 commit 39.g56c9900 in Dec 14 2015"""


    global last_updateContext
    if args:
        if args[0] == 'http://mock.iota.com:1026/v1/updateContext':
            jsobj_1 = json.loads(kwargs["data"])
            last_updateContext = jsobj_1['contextElements'][0]
            return MockResponse("", 201)
        elif args[0] == 'http://mock.iota.com:1026/v1/queryContext':
            res1 = { }
            res1["contextElement"] = last_updateContext
            response = {"contextResponses" : [] }
            response["contextResponses"].append(res1)
            return MockResponse(json.dumps(response), 200)
        elif args[0] == 'http://mock.cb.com:1026/v1/contextEntities/Sala01':
            response = { }
            response["contextElement"] = last_updateContext
            return MockResponse(json.dumps(response), 200)
        elif args[0] == 'http://mock.iota.com:1026/iot/about':
            return MockResponse(version, 200)

    return MockResponse("not found " + kwargs["url"], 404)

def mocked_requests_post(*args, **kwargs):

    nodata = """{"reason": "Malformed header","details": "Fiware-Service not accepted - a service string must not be longer than 50 characters and may only contain underscores and alphanumeric characters and lowercase"}"""

    return MockResponse(nodata, 400)


class IOTAUtilsTest(unittest.TestCase):

   def setUp(self):
      self.iota = Rest_Utils_IoTA(server_root="http://mock.iota.com:1026/iot", server_root_secure="http://mock.iota.com:1026/iot")
      #self.iota = Rest_Utils_IoTA(server_root="http://10.95.213.36:8080/iot", server_root_secure="http://10.95.213.36:8080/iot")


   @mock.patch('requests.get', side_effect=mocked_requests_get)
   def test_version(self, mock_requests):
       version="1.0.0"
       #version = self.iota.version()
       print "### Test ---> Version: " + version
       #assert_in("Welcome to IoTAgents", version.content, msg="bad data returned to query version to IOTA")
       #assert_in("identifier:IoTPlatform:8080", version.content, msg="bad data returned to query version to CB")

   @mock.patch('requests.post', side_effect=mocked_requests_post)
   def tes_bad_create_service(self, mock_requests):
       res = self.iota.create_service(service_name="kk<xx>", protocol="bad<protoxol>" )
       print "### Test ---> Bade service name: " + res.content
       eq_(400, res.status_code, msg="version to CB does not return 200")
       assert_in("a service string must not be longer than 50 characters and may only contain underscores and alphanumeric characters", res.content, msg="bad data returned to bad sewrvice name to IOTA")

if __name__ == '__main__':
    unittest.main()


