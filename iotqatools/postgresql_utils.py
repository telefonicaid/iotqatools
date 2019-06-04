# -*- coding: utf-8 -*-
"""
Copyright 2019 Telefonica Spain

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
__author__ = 'Thinking Cities Team'


import psycopg2
import gc

# constants
EMPTY = u''
WITHOUT = u'without'

# postgresql commands
SELECT_VERSION = u'SELECT version ()'
POSTGRESQL_CREATE_DATABASE = u'CREATE DATABASE IF NOT EXISTS '
POSTGRESQL_CREATE_TABLE = u'CREATE TABLE IF NOT EXISTS '
POSTGRESQL_DROP_DATABASE = u'DROP SCHEMA IF EXISTS '
POSTGRESQL_DROP_TABLE = u'DROP TABLE '
POSTGRESQL_SHOW_DATABASE = u'SHOW DATABASES'
POSTGRESQL_SHOW_TABLES = u'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \''


class Postgresql:
    """
    postgresql functionality
    """

    def __init__(self, **kwargs):
        """
        constructor
        :param host: postgresql host (MANDATORY)
        :param port: postgresql port (MANDATORY)
        :param user: postgresql user (MANDATORY)
        :param password:  postgresql pass (MANDATORY)
        :param database: postgresql database (OPTIONAL)
        :param version: postgresql version (OPTIONAL)
        :param postgresql_verify_version: determine whether the version is verified or not (True or False). (OPTIONAL)
        :param capacity: capacity of the channel (OPTIONAL)
        :param channel_transaction_capacity: amount of bytes that can be sent per transaction (OPTIONAL)
        :param retries_number: number of retries when get values (OPTIONAL)
        :param delay_to_retry: time to delay each retry (OPTIONAL)
        """
        self.host = kwargs.get("host", EMPTY)
        self.port = kwargs.get("port", EMPTY)
        self.user = kwargs.get("user", EMPTY)
        self.password = kwargs.get("password", EMPTY)
        self.database = kwargs.get("database", EMPTY)
        self.version = kwargs.get("version", "2,2")
        self.postgresql_verify_version = kwargs.get("psql_verify_version", "false")
        self.capacity = kwargs.get("capacity", "1000")
        self.transaction_capacity = kwargs.get("transaction_capacity", "100")
        self.retries_number = int(kwargs.get('retries_number', 1))
        self.retry_delay = int(kwargs.get('delay_to_retry', 10))
        self.conn = None

    def __error_assertion(self, value, error=False):
        """
        It Shows exception error or return for evaluation
        :param value: exception error text
        :param error: True or False (True - return per evaluation |False shows the exception error)
        :return: exception error text
        """
        if error:
            return value
        assert False, value

    def __query(self, sql, error=False):
        """
        new query
        :param sql: query
        :return: message as text
        """
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            return cur
        except Exception, e:
            return self.__error_assertion('DB exception: %s' % (e), error)

    def __drop_database(self):
        """
        delete a database
        """
        self.__query("%s `%s`" % (POSTGRESQL_DROP_DATABASE, self.database))  # drop database

    # public methods ------------------------------------------
    def connect(self):
        """
        Open a new postgresql connection
        """
        try:
            self.database = EMPTY
            self.conn = psycopg2.connect("dbname=%s user=%s host=%s password=%s" % (self.database, self.user, self.host, self.password))
        except Exception, e:
            return self.__error_assertion('DB exception: %s' % (e))

    def set_database(self, database):
        """
        set database name
        """
        self.database = database

    def disconnect(self):
        """
        Close a postgresql connection and drop the database before
        """
        self.__drop_database()
        self.conn.close()  # close postgresql connection
        gc.collect()  # invoking the Python garbage collector

    def get_version(self):
        """
        :return: returns postgresql version
        """
        try:
            self.conn = psycopg2.connect("dbname=%s user=%s host=%s password=%s" % (self.database, self.user, self.host, self.password))
        except Exception, e:
            return self.__error_assertion('DB exception: %s' % (e))
        cur = self.__query(SELECT_VERSION)
        row = cur.fetchone()
        return str(row[0])

    def verify_version(self):
        """
        Verify if the postgresql version is the expected
        """
        if self.postgresql_verify_version.lower() == "true":
            cur = self.__query(SELECT_VERSION)
            row = cur.fetchone()
            assert row[0] == self.version, \
                "Wrong version expected: %s. and version installed: %s" % (str(self.version), str(row[0]))

    def create_database(self, name):
        """
        create a new Database
        :param name:
        """
        self.database = name.lower()  # converted to lowercase, because cygnus always convert to lowercase per ckan
        self.__query("%s `%s` %s;" % (POSTGRESQL_CREATE_DATABASE, self.database, "DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci"))

    def drop_database(self, name):
        """
        create a new Database
        :param name:
        """
        self.database = name.lower()  # converted to lowercase, because cygnus always convert to lowercase per ckan
        self.__query("%s `%s`;" % (POSTGRESQL_DROP_DATABASE, self.database))

    def generate_field_datastore_to_resource(self, attributes_number, attributes_name, attribute_type, metadata_type):
        """
        generate fields to datastore request
        :return: fields list
        """
        field = " (recvTime text"
        for i in range(int(attributes_number)):
            if attribute_type != WITHOUT: field = field + ", " + attributes_name + "_" + str(i) + " " + attribute_type
            if metadata_type != WITHOUT: field = field + ", " + attributes_name + "_" + str(i) + "_md " + metadata_type
        return field + ")"

    def create_table(self, name, database_name, fields):
        """
        create a new table per column type
        :param name:
        :param database_name:
        :param fields:
        """
        self.table = name
        self.__query("%s `%s`.`%s` %s;" % (POSTGRESQL_CREATE_TABLE, database_name, self.table, fields))

    def drop_table(self, name, database_name):
        """
        create a new table per column type
        :param name:
        :param database_name:
        :param fields:
        """
        self.table = name
        self.__query("%s `%s`.`%s`;" % (POSTGRESQL_DROP_TABLE, database_name, self.table))


    def table_exist(self, database_name, table_name):
        """
        determine if table exist in database
        :param database_name:
        :param table_name:
        """
        cur = self.__query(
            'SELECT table_name FROM information_schema.tables WHERE table_schema = "%s" AND table_name = "%s" LIMIT 1;' % (
                database_name, table_name))
        return cur.fetchone()

    def table_search_one_row(self, database_name, table_name):
        """
        get last record from a table
        :param database_name:
        :param table_name:
        """
        if self.table_exist(database_name, table_name) != None:
            cur = self.__query('SELECT * FROM `%s`.`%s` ORDER BY 1 DESC LIMIT 1;' % (database_name, table_name))
            return cur.fetchone()  # return one row from the table
        return False

    def table_search_several_rows(self, database_name, table_name, rows):
        """
        get last records from a table
        :param database_name:
        :param table_name:
        :param rows: (moved to the last value to maintain the order of priority params)

        """
        if self.table_exist(database_name, table_name) != None:
            cur = self.__query('SELECT * FROM `%s`.`%s` ORDER BY 1 DESC LIMIT %s;' % (database_name, table_name, rows))

            return cur.fetchall()  # return several lines from the table
        return False

    def table_search_columns_in_several_rows(self, database_name, table_name, rows, columns):
        """
        get last record rows from a table for some columns
        :param database_name:
        :param table_name:
        :param rows: (moved to the last value to maintain the order of priority params)
        :param columns:
        """
        if self.table_exist(database_name, table_name) != None:
            cur = self.__query(
                'SELECT `%s` FROM `%s`.`%s` ORDER BY 1 DESC LIMIT %s;' % (columns, database_name, table_name, rows))

            return cur.fetchall()  # return several lines from the table
        return False

    def table_search_columns_last_row(self, database_name, table_name, columns):
        """
        get last row from a table and some columns
        :param database_name:
        :param table_name:
        :param columns:
        """
        if self.table_exist(database_name, table_name) != None:
            cur = self.__query('SELECT %s FROM `%s`.`%s` ORDER BY 1 DESC LIMIT 1;' % (columns, database_name, table_name))
            row = cur.fetchone()
            if (row == None or row[0] == None):
                cur = self.__query('SELECT attrValue FROM `%s`.`%s` WHERE attrName = \'%s\' ORDER BY 1 DESC LIMIT 1;' % (database_name, table_name, columns))
                row = cur.fetchone()
            return row
        return False

    def table_pretty_output(self, database_name, table_name):
        cur = self.__query('SELECT * FROM `%s`.`%s` ORDER BY 1 DESC LIMIT 1;' % (database_name, table_name))
        results = cur.fetchall()
        empty_values = []
        width = []
        cols = []
        tavnit = '|'
        separator = '+'
        rows = []
        for elements in results:
            tup = elements
            for element in tup:
                if element is None:
                    empty_values.append(True)
                else:
                    empty_values.append(False)
                    rows.append(element)
        count = 0
        rows = tuple(rows)
        for cd in cur.description:
            if count in empty_values and empty_values[count] is False:
                width.append(max(cd[2], len(cd[0])))
                cols.append(cd[0])
            count += 1
        for w in width:
            tavnit += " %-"+"%ss |" % (w,)
            separator += '-'*w + '--+'

        ## TODO: Use the logger for this @Andrea
        print(separator)
        print(tavnit % tuple(cols))
        print(separator)
        # FIXME: Disable by "TypeError: not all arguments converted during string formatting"
        #print(tavnit % rows)
        #print(separator)

    def get_table_records(self, database_name, table_name):
        """
        get last row from a table and some columns
        :param database_name:
        :param table_name:
        """
        if self.table_exist(database_name, table_name) != None:
            cur = self.__query('SELECT * FROM `%s`.`%s`;' % (database_name, table_name))
            return cur.rowcount  # return the number of records of the table
        return False
