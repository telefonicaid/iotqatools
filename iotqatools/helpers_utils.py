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
__author__ = 'Iván Arias León (ivan dot ariasleon at telefonica dot com)'

import json
import random
import string
import time
import xmltodict
import datetime
import hashlib
import logging
import math
from decimal import Decimal
import operator



# general constants
EMPTY = u''
XML = u'xml'
JSON = u'json'

__logger__ = logging.getLogger("utils")


def string_generator(size=10, chars=string.ascii_letters + string.digits):
    """
    Method to create random strings
    :param size: define the string size
    :param chars: the characters to be use to create the string
    return random string
    """
    return ''.join(random.choice(chars) for x in range(size))


def number_generator(size=5, decimals="%0.1f"):
    """"
    Method to create random number
    :param decimals: decimal account
    :param size: define the number size
    :return: random float
    """
    return float(decimals % (random.random() * (10**size)))


def convert_str_to_bool(value):
    """
    convert string to boolean
    :return boolean
    """
    if type(value) == str or type(value) == unicode:
        return value.lower() in ("yes", "true", "t", "1", "y")
    return value


def convert_str_to_dict(body, content):
    """
    Convert string to Dictionary
    :param body: String to convert
    :param content: content type (json or xml)
    :return: dictionary
    """
    try:
        if content == XML:
            return xmltodict.parse(body)
        else:
            return json.loads(body)
    except Exception, e:
        assert False,  " ERROR - converting string to %s dictionary: \n" \
                       "  %s \n  " \
                       "  Exception error: %s" % (str(content), str(body), str(e))


def convert_dict_to_str(body, content):
    """
    Convert Dictionary to String
    :param body: dictionary to convert
    :param content: content type (json or xml)
    :return: string
    """
    try:
        if content == XML:
            return xmltodict.unparse(body)
        else:
            return str(json.dumps(body, ensure_ascii=False).encode('utf-8'))
    except Exception, e:
        assert False,  " ERROR - converting %s dictionary to string: \n" \
                       "  %s \n" \
                       "  Exception error: %s" % (str(content), str(body), str(e))


def convert_str_to_list(text, separator):
    """
    Convert String to list
    :param text: text to convert
    :param separator: separator used
    :return: list []
    """
    try:
        return text.split(separator)
    except Exception, e:
        assert False,  " ERROR - converting %s string to list with separator: %s \n" \
                       "   Exception error:%s" % (str(text), str(separator), str(e))


def convert_list_to_string(list, separator):
    """
    Convert  List to String
    :param list: list to convert
    :param separator: separator used
    :return: string ""
    """
    try:
        return separator.join(list)
    except Exception, e:
        assert False,  " ERROR - converting list to string with separator: %s \n" \
                       "    Exception error:%s" % (str(separator), str(e))


def show_times(init_value):
    """
    shows the time duration of the entire test
    :param init_value: initial time
    """
    print "**************************************************************"
    print "Initial (date & time): " + str(init_value)
    print "Final   (date & time): " + str(time.strftime("%c"))
    print "**************************************************************"


def generate_timestamp(**kwargs):
    """
    generate timestamp or convert from a date with a given format
    ex: 1425373697
    :param date: date to convert to timestamp, if it does not exist, returns current time
    :param format: date format
    :param utc: determine whether the timestamp is in utc time or not
    :return  timestamp
    """
    date = kwargs.get("date", EMPTY)
    format = kwargs.get("format", "%Y-%m-%dT%H:%M:%S.%fZ")
    utc = kwargs.get("utc", False)

    UTC_OFFSET_TIMEDELTA = ((datetime.datetime.utcnow() - datetime.datetime.now()).total_seconds())
    if date == EMPTY:
        local_time = time.time()
    else:
        local_time = time.mktime(datetime.datetime.strptime(date, format).timetuple())
    if utc:
        return local_time - UTC_OFFSET_TIMEDELTA
    return local_time


def generate_date_zulu(timestamp=0):
    """
    convert timestamp or generate to date & time zulu (UTC)
    ex: 2014-05-06T10:39:47.696Z
    :return date-time zulu formatted (UTC)
    """
    if timestamp == 0:
        timestamp = generate_timestamp()
    return str(datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))


def get_date_only_one_value(date, value):
    """
    get only one specific value in a date-time
    :param date: date-time to get one specific value
    :param value: value to return ( year | month | day | hour | minute | second)
    :return string
    """
    dupla = {"year": "%Y", "month": "%m", "day": "%d", "hour": "%H", "minute": "%M", "second": "%S"}
    for value_in_dupla in dupla:
        if value_in_dupla == value.lower():
            return datetime.datetime.fromtimestamp(date).strftime(dupla[value_in_dupla])


def is_an_integer_value(value):
    """
    verify if a number is integer or not, verifying if the decimal part is equal to zero
    :param value: value to check
    :return: boolean (True is integer | False is float )
    """
    try:
        temp_value = Decimal(value)  # Cannot convert float to Decimal.  First convert the float to a string
        dec_v, int_v = math.modf(temp_value)
        if dec_v == 0:
            return True
        return False
    except Exception, e:
        assert False, " Error - %s is not numeric... \n %s" % (str(value), str(e))


def generate_hash_sha512(input, limit=-1):
    """
    generate hash algorithms SHA512
    :param input: text to generate secure hash
    :param limit: number of digit returned (if -1 returns all digits (128))
    :return string
    """
    hash_resp = hashlib.sha512(input).hexdigest()
    if limit == -1:
        limit = len(hash_resp)
    return hash_resp[0:limit]


def mapping_quotes(attr_value):
        """
        limitation in lettuce and behave change \' by " char
        """
        temp = ""
        for i in range(len(attr_value)):
            if attr_value[i] == "\'":
                temp = temp + "\""
            else:
                temp = temp + attr_value[i]
        return temp


def remove_quote(text):
    """
    remove first and last characters if they are quote
    :param text:
    :return: text type
    """
    if isinstance(text, basestring):
        text = text.lstrip('"')
        text = text.rstrip('"')
    return text


def read_file_to_json(file_name):
    """
    read a file and return a dictionary
    :param file_name: file to read (path included)
    :return: dict
    """
    try:
        with open(file_name) as config_file:
            return json.load(config_file)
    except Exception, e:
        raise Exception("\n ERROR - parsing the %s file\n     msg= %s" % (file_name, str(e)))


def get_operator_fn(op):
    """
    return an operation from string
    https://docs.python.org/2/library/operator.html#
    :param op: operator in string
    :return: operator
    """
    return {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.div,
        '%': operator.mod,
        '^': operator.xor,
        '==':operator.eq,
        '!=':operator.ne,
        '>=':operator.ge,
        '<=':operator.le,
        '>':operator.gt,
        '<':operator.lt
        }[op]


def eval_binary_expr(op1, operator, op2):
    """
    evaluate a binary expression
    :param op1: value 1
    :param operator: operator
    :param op2: value 2
    :return: value or boolean
    """
    if operator not in ['==', '!=']:
        try:
            op1, op2 = int(float(op1)), int(float(op2))
        except Exception, e:
            __logger__.warn("Some value is not a numeric format. (%s)" % str(e))
            return False
    return get_operator_fn(operator)(op1, op2)


def find_list_in_string (chars_list, text):
    """
    find a chars list into a text. Ex: [".", "$"]
    return int
    """
    for item in chars_list:
        temp = text.find(item)
        if temp >= 0:
            return temp
    return -1
