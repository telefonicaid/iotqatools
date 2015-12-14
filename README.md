# iot-qa-tools [![Build Status](https://travis-ci.org/telefonicaid/iot-qa-tools.svg?branch=develop)](https://travis-ci.org/telefonicaid/iot-qa-tools) [![Coverage Status](https://coveralls.io/repos/telefonicaid/iot-qa-tools/badge.svg?branch=develop&service=github)](https://coveralls.io/github/telefonicaid/iot-qa-tools?branch=develop) [![StackOverflow](http://b.repl.ca/v1/help-stackoverflow-orange.png)]  (https://stackoverflow.com/questions/tagged/iot-qa-tools) 
    
Common IoT tools and libs used by QA



## Overview

Internet of Things Platform Quality Assurance Tools (aka IoTP QA-Tools).

This is a common project set up to share and reuse code, tools by the Quality Assurance.
This library tries to help you to develop, maintain and publish the code developed in a common repository.

## Installation

This library can be installed directly with a GitHub repository dependency. To install it locally, type the
following command (we strongly recommend you to use virtual environments):

*Stable version*

```
$ pip install git+https://github.com:telefonicaid/iot-qa-tools@@master
```

*Last version*

```
$ pip install git+https://github.com:telefonicaid/iot-qa-tools@develop
```

*Specific version*

```
$ pip install git+https://github.com:telefonicaid/iot-qa-tools@picked_tag
```

NOTES:
 - You may need to set GIT_SSL_NO_VERIFY=true environment variable in your machine
 - You should add "--upgrade" (if you have a previous installed version of this library)


## Developers installation

After cloning this repository:

```
$ git clone git@github.com:telefonicaid/iot-qa-tools.git
```

You can install the basic dependencies using the setup.py:

```
$ python setup.py install
```


You should install the dependencies:

```
(basic) pip install -r iotqautils/requirements.txt
```

And you are ready to play with it!

## Adding a module

In order to add a module to the library follow this steps:
* Create the appropriate files (module_utils.py or module_tools.py file in the iotqatools folder.
* In the setup.py file, in the `py_modules` attribute, add the name of the module (without the extension).
* In the requirements.txt file, add the required 3rd party libs that your module needs. This dependencies will be automatically installed when the library is installed.

## Using a module
Example of using a module after install it

* Import a module:

```
python
from iotqatools.cb_utils import CBUtils
```

* Initialise it:

```
 cb = CBUtils(instance='127.0.0.1', verbosity=1)
```

* Use it:
```
print cb.version()
    <Response [200]>
print cb.version().content
    {
      "orion" : {
      "version" : "0.16.0_20141126090713",
      "uptime" : "1 d, 3 h, 0 m, 38 s",
      "git_hash" : "15153252ddf66e673987443b7f9e9e1194577d29",
      "compile_time" : "Wed Nov 26 09:09:45 CET 2014",
      "compiled_by" : "develenv",
      "compiled_in" : "ci-fiware-01"
    }
}
```


* Create a entity in CB

```
 data0 = dict({'ent_type': 'Sala','ent_pattern': 'false', 'ent_id': 'Sala01',
	'attributes': "[{'name': 'temperature', 'type': 'centigrade', 'value': '99'}]"})
 cb.entity_append('x222', data0)
     SUT: CB
     SENT REQUEST URL: http://qa-orion-fe-02:1026/NGSI10/updateContext
     SENT REQUEST HEADERS:
 {'Accept': 'application/json',
 'Fiware-Service': 'x222',
 'content-type': 'application/json'}
     SENT REQUEST DATA: {
        "contextElements": [
            {
                "type": "Sala",
                "isPattern": "false",
                "id": "Sala01",
                "attributes": [{"name": "temperature", "type": "centigrade", "value": "99"}]
            }],
        "updateAction": "APPEND"
    }
     RESPONSE CODE: 200
     RESPONSE HEADER:
 {'content-length': '402',
 'content-type': 'application/json',
 'date': 'Thu, 27 Nov 2014 12:13:58 GMT',
 'width': 20}
     RESPONSE BODY: {
  "contextResponses" : [
    {
      "contextElement" : {
        "type" : "Sala",
        "isPattern" : "false",
        "id" : "Sala01",
        "attributes" : [
          {
            "name" : "temperature",
            "type" : "centigrade",
            "value" : ""
          }
        ]
      },
      "statusCode" : {
        "code" : "200",
        "reasonPhrase" : "OK"
      }
    }
  ]
}
```


* Create a subscription:

```
 subs0 = dict({'ent_type': 'Sala','ent_pattern': 'false', 'ent_id': 'Sala99' ,'notify_url': 'http://localhost:5050/notify'})
 sub = cb.subscription_add('x222',templateData=subs0)
     SUT: CB
     SENT REQUEST URL: http://qa-orion-fe-02:1026/NGSI10/subscribeContext
     SENT REQUEST HEADERS:
 {'Accept': 'application/json',
 'Fiware-Service': 'x222',
 'content-type': 'application/json'}
     SENT REQUEST DATA: {
        "entities": [
            {
                "type": "Sala",
                "isPattern": "false",
                "id": "Sala99"
            }
        ],
        "attributes": [],
        "reference": "http://localhost:5050/notify",
        "duration": "PT5M",
        "notifyConditions": [
            {
                "type": "ONCHANGE",
                "condValues": [
                    "temperature"
                ]
            }
        ]
    }
     RESPONSE CODE: 200
     RESPONSE HEADER:
 {'content-length': '109',
 'content-type': 'application/json',
 'date': 'Thu, 27 Nov 2014 12:15:13 GMT',
 'width': 20}
     RESPONSE BODY: {
  "subscribeResponse" : {
    "subscriptionId" : "547715d198e0d9b003139fa2",
    "duration" : "PT5M"
  }
}
```


Requirements
------------

Python 2.7.4 (http://www.python.org)

distribute 0.6.36 (https://pypi.python.org/pypi/distribute)

pip 1.3.1 (https://pypi.python.org/pypi/pip)

Installation
------------

Configure a virtual environment with the required packages

NOTE: You may need to set GIT_SSL_NO_VERIFY=true environment variable in your machine

Library Summary
---------------
```
ac_utils
cb_utils
cb_v2_utils
cep_utils
helpers_utils
iota_utils
orchestator_utils
sth_utils
ks_utils
pep_utils
iot_tools
iot_logger
```


License
---------

( c ) 2013-2015 Telefónica I+D, GNU Affero General Public License


