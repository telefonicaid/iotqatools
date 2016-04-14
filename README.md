# iotqatools [![Build Status](https://travis-ci.org/telefonicaid/iotqatools.svg?branch=develop)](https://travis-ci.org/telefonicaid/iotqatools) [![Coverage Status](https://coveralls.io/repos/telefonicaid/iotqatools/badge.svg?branch=develop&service=github)](https://coveralls.io/github/telefonicaid/iotqatools?branch=develop) [![StackOverflow](http://b.repl.ca/v1/help-stackoverflow-orange.png)]  (https://stackoverflow.com/questions/tagged/iotqatools) 
    
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
$ pip install git+https://github.com/telefonicaid/iotqatools@master
```

*Last version*

```
$ pip install git+https://github.com/telefonicaid/iotqatools@develop
```

*Specific version*

```
$ pip install git+https://github.com/telefonicaid/iotqatools@picked_tag
```

NOTES:
 - You may need to set GIT_SSL_NO_VERIFY=true environment variable in your machine
 - You should add "--upgrade" (if you have a previous installed version of this library)


## Developers installation

After cloning this repository:

```
$ git clone git@github.com:telefonicaid/iotqatools.git
```

You can install the basic dependencies using the setup.py:

```
$ python setup.py install
```


You should install the dependencies:

```
(basic) pip install -r requirements.txt
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
      "version" : "0.26.0_20141126090713",
      "uptime" : "1 d, 3 h, 0 m, 38 s",
      "git_hash" : "15153252ddf66e673987443b7f9e9e1194577d29",
      "compile_time" : "Wed Nov 26 09:09:45 CET 2014",
      "compiled_by" : "develenv",
      "compiled_in" : "ci-fiware-01"
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
sth_utils.py
remote_log_utils.py
pep_utils.py
orchestator_utils.py
mysql_utils.py
mongo_utils.py
ks_utils.py
iota_utils.py
iota_measures.py
iot_tools.py
iot_logger.py
helpers_utils.py
fabric_utils.py
ckan_utils.py
cep_utils.py
cb_v2_utils.py
cb_utils.py
ac_utils.py

```


License
---------

( c ) 2013-2016 Telefónica I+D, GNU Affero General Public License


