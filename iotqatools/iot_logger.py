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

__author__ = 'xvc'

import logging


def get_logger(name, level='DEBUG', verbose=False, file=False, filename='', formatter=None):
    """
    :param name: Name of the logging module
    :param level: Verbosity level (default DEBUG). Possible values ['CRITICAL','ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')
    :param verbose: Formatter adds time and logger name to log info. True for verbose active (default False).
    :param file: Create/update the logger adding a File handler
    :param filename: If file is True, indicate the filename
    :param formatter: Specific logging.Formatter, if its none or is not a formatter class, default depending of the verbose is used
    :return: a Logger object with the iot default formatter and the verbosity level especified
    """
    # Create logger
    logger = logging.getLogger(name)
    # Do not pass throw parents handlers
    logger.propagate = False
    try:
        logger.setLevel(level)
    except ValueError as e:
        get_logger(__name__, 'ERROR').error(str(e))
        return
    # If there is a handler with the same class, delete it first
    if len(logger.handlers) > 0:
        for handler in logger.handlers:
            if file:
                if isinstance(handler, logging.FileHandler):
                    logger.removeHandler(handler)
            else:
                if isinstance(handler, logging.StreamHandler):
                    logger.removeHandler(handler)
    if file:
        if filename == '':
            filename_log = '{name}.log'.format(name=__name__)
        else:
            if not filename.endswith('.log'):
                filename_log = '{filename}.log'.format(filename=filename)
            else:
                filename_log = filename
        new_handler = logging.FileHandler(filename_log)
    else:
        new_handler = logging.StreamHandler()

    new_handler.setLevel(level)

    # Create formatter or use one passed
    if formatter is not None and isinstance(formatter, logging.Formatter):
        new_formatter = formatter
    else:
        if verbose:
            new_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            new_formatter = logging.Formatter('%(levelname)s %(message)s')

    # Set formatter
    new_handler.setFormatter(new_formatter)

    # Add new handler with the new format to the logger
    logger.addHandler(new_handler)
    return logger

