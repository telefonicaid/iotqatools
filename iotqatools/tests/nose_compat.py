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
__author__ = '_tme_'

def eq_(a, b, msg=None):
    assert a == b, msg

def ok_(expr, msg=None):
    assert expr, msg

def assert_true(expr, msg=None):
    assert expr, msg

def assert_in(member, container, msg=None):
    assert member in container, msg

def assert_not_in(member, container, msg=None):
    assert member not in container, msg

def assert_not_equal(a, b, msg=None):
    assert a != b, msg

def assert_greater_equal(a, b, msg=None):
    assert a >= b, msg
