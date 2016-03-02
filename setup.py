#!/usr/bin/env python
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

import os
import sys
import re
import setuptools.command.build_py
from setuptools import setup, find_packages, Command


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            # TODO support version numbers
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        elif re.match(r'\s*-r\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    return dependency_links


def get_requirements(filename):
    return open(filename).read().splitlines()


readme = []
with open('README.md', 'r') as fh:
    readme = fh.readlines()

req = get_requirements('requirements.txt')
req_dev = get_requirements('requirements.txt')

setup(
    name='iotqatools',
    version='0.1.17',
    description='Iot QA Tools',
    url='https://github.com/telefonicaid/iot-qa-tools',
    author='Telefonica I+D',
    zip_safe=False,
    long_description='\n'.join(readme),
    install_requires=req,
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Development',
        'Framework :: Behave',
        'Intended Audience :: Developers',
        'Intended Audience :: Quality Assurance',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7'
    ],
    py_modules=[
        'iotqatools.iot_logger',
        'iotqatools.ac_utils',
        'iotqatools.cb_utils',
        'iotqatools.cb_v2_utils',
        'iotqatools.cep_utils',
        'iotqatools.fabric_utils',
        'iotqatools.helpers_utils',
        'iotqatools.iot_tools',
        'iotqatools.iota_utils',
        'iotqatools.ks_utils',
        'iotqatools.mongo_utils',
        'iotqatools.orchestator_utils',
        'iotqatools.pep_utils',
        'iotqatools.sth_utils'  
    ],
    packages=[
        'iotqatools',
        'iotqatools.templates'
    ],
)
