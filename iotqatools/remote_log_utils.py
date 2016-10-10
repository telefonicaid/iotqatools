# -*- coding: utf-8 -*-
"""
Copyright 2016 Telefonica Investigación y Desarrollo, S.A.U

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


import os

from iotqatools.helpers_utils import *

__logger__ = logging.getLogger("utils")

# constants
FILE                  = u'file'
FILE_DEFAULT          = u'file.log'
FABRIC                = u'fabric'
OWNER_GROUP_DEFAULT   = u'root'
OWNER                 = u'owner'
GROUP                 = u'group'
MOD                   = u'mod'
MOD_DEFAULT           = u'777'

class Remote_Log:
    """
    manage remote log
    """

    def __init__(self, **kwargs):
        """
        constructor
        :param file: log file
        :param fabric: instance from tools.fabric_utils import FabricSupport
            ex: myfab = FabricSupport(host=host,
                                      user=user,
                                      password=password,
                                      cert_file=cert_file,
                                      retry=error_retry,
                                      hide=True,
                                      sudo=sudo_cygnus)
        """
        file_path   = kwargs.get(FILE, FILE_DEFAULT)
        self.fabric = kwargs.get(FABRIC, None)

        try:
            if self.fabric is not None:
                temp = os.path.split(file_path)  # split the path and the file of the file and path together
                self.file = temp[1]
                path = temp[0]
                self.fabric.current_directory(path)
        except Exception, e:
            __logger__.error("ERROR - in log file... \n      - %s" % str(e))

    def delete_log_file(self):
        """
        delete file log
        """
        self.fabric.run("rm %s" % (self.file))

    def create_log_file(self, **kwargs):
        """
        create a log file
        :param owner: file owner
        :param group: group ownership of the file
        :param mod: file permissions. Mode can be specified with octal numbers or with letters.
        """
        owner = kwargs.get(OWNER, OWNER_GROUP_DEFAULT)
        group = kwargs.get(GROUP, OWNER_GROUP_DEFAULT)
        mod   = kwargs.get(MOD, MOD_DEFAULT)

        self.fabric.run("echo '' > %s" % self.file)
        self.fabric.run("chown %s:%s %s" % (owner, group, self.file))
        self.fabric.run("chmod %s %s" % (mod, self.file))

    def find_line(self, label, text):
        """
        find the last occurrence in log with a label and a text
        steps:
           - first, seek all lines with this label
           - second, invest the lines list (first lines last)
           - third, return the last line with the text expected
        :param label: label to find
        :param text: text to find
        :return: line found or None
        """
        __logger__.debug("label: \"%s\" and text: \"%s\" seeked in the log file: %s" % (label, text, self.file))
        label_list = []
        log_lines = self.fabric.read_file(self.file)
        log_lines_list = convert_str_to_list(log_lines, "\n")
        for line in log_lines_list:  # find all lines with the label
            if line.find("lvl=%s" % label)>= 0:
                label_list.append(line)
        label_list.reverse() # list reverse because looking for the last occurrence
        for line in label_list:
            if line.find(text) >= 0:
                return line
        return None

    def get_trace(self, line, trace):
        """
        get trace from log line
        :param line: line to search
            ex:   time=2016-03-17T16:49:54.122CET | lvl=INFO | trans=1458224454-818-00000000665 | srv=pending | subsrv=pending | from=pending | function=lmTransactionStart | comp=Orion | msg=logMsg.h[1803]: Starting transaction from 10.95.233.161:58375/v2/entities       :return. date-time zulu (string)
        :param trace in line.
        :return string
        """
        trace_error = u'"%s" trace does not exist on the line' % trace
        ls = line.split("|")
        for param in ls:
            if param.find("%s=" % trace) >= 0:
                d = param.split("=")[1][:-1] # the string has an empty character on the end
                __logger__.debug(u'the "%s" trace has "%s" as value' % (trace, d))
                return d
        __logger__.warn(trace_error)
        return trace_error




