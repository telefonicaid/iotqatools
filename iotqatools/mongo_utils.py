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

import time
import logging
import pymongo


# constants
EMPTY = u''
BUILD_INFO = u'buildInfo'

__logger__ = logging.getLogger("utils")


class Mongo:
    """
    Mongo Management Class
    """

    def __init__(self,  **kwarg):
        """
        constructor class
        :param host:  mongo hostname
        :param port: mongo port
        :param user:  mongo username
        :param password: password associated to mongo username
        :param version: mongo version
        :param verify_version: determine if the mongo version is verified ( true |false )
        :param database: mongo current database
        :param collection: mongo current collection
        :param retries: number of retries when find documents
        :param retry_delay: delay en each retry when find documents
        """
        self.host = kwarg.get(u'host', u'localhost')
        self.port = kwarg.get(u'port', u'27017')
        self.user = kwarg.get(u'user', EMPTY)
        self.password = kwarg.get(u'password', EMPTY)
        self.version = kwarg.get("version", EMPTY)
        self.verify_version = kwarg.get(u'verify_version', EMPTY)
        self.database_name = kwarg.get(u'database', u'test_mongo')
        self.collection_name = kwarg.get(u'collection', EMPTY)
        self.retries = kwarg.get(u'retries', 1)
        self.retry_delay = kwarg.get(u'retry_delay', 1)
        self.current_collection = None

    def connect(self, database=EMPTY):
        """
        connect to mongo
        :param database: database to connect
        Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
        """
        if database != EMPTY:
            self.database_name = database
        self.mongo_uri = "mongodb://%s:%s/%s" % (self.host, self.port, self.database_name)
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.current_database = self.client.get_default_database()
            if self.collection_name != EMPTY:
                self.current_collection = self.current_database[self.collection_name]
        except Exception, e:
            assert False, " ERROR - Connecting to MongoDB...\n %s " % (str(e))

    def execute_command(self, command):
        """
        execute a command in mongo
        :param command: command to execute
        :return: dict
        """
        try:
            return self.current_database.command(command)
        except Exception, e:
            assert False, " ERROR - Executing command \"%s\" in MongoDB...\n %s " % (command, str(e))

    def eval_version(self, version=EMPTY):
        """
        Evaluate if  the version in mongo is the expected
        and if verify version variable is true
        :return string
        """
        if self.verify_version.lower() == "true":
            if version == EMPTY: version = self.version
            mongo_version = self.execute_command(u'buildInfo')[u'version']
            if mongo_version != version:
                return u' ERROR - in mongo version: \"%s\" expected and \"%s\" installed...' % (version, mongo_version)
            return u'OK'

    def get_current_connection(self):
        """
        get current connection data (host, port, database. collection)
        :return: collection dict or None
        """
        return self.current_collection

    def choice_collection(self, name):
        """
        Access to another collection in the current database
        :param name: collection name
        """
        try:
            self.collection_name = name
            self.current_collection = self.current_database[name]
        except Exception, e:
            assert False, " ERROR - Accessing to collection %s in MongoDB...\n %s" % (name, str(e))

    def insert_data(self, data):
        """
        Insert a new document in a collection
        """
        try:
            self.current_collection.insert(data)
        except Exception, e:
            assert False, " ERROR - Inserting data into %s in MongoDB...\n %s" % (str(self.current_collection), str(e))

    def update_data(self, data, query={}):
        """
        update a document in a collection using a query
        """
        try:
            self.current_collection.update(query, data)
        except Exception, e:
            assert False, " ERROR - Updating data in a collection %s in MongoDB...\n %s" % (self.current_collection, str(e))

    def find_data(self, query={}):
        """
        find a set of data in the current collection using a collection
        :param query: query to find
        :return: cursor
        """
        try:
            return self.current_collection.find(query)
        except Exception, e:
            assert False, " ERROR - Searching data from a collection %s in MongoDB...\n %s" % (self.current_collection, str(e))

    def find_with_retry(self, query={}):
        """
        find documents with retries defined
        :param query: query to find
        :return: cursor
        """
        c = 0
        cursor = None
        for i in range(int(self.retries)):
            cursor = self.find_data(query)
            if cursor.count() != 0:
                return cursor
            c += 1
            print " WARN - Retry in find documents in Mongo. No: (%s)" % str(c)
            time.sleep(self.retry_delay)
        return cursor

    def get_cursor_value(self, cursor):
        """
        get documents into a cursor
        :param cursor:
        :return: list
        """
        temp_list = []
        for doc in cursor:
            temp_list.append(doc)
        return temp_list

    def print_cursor(self, cursor):
        """
        print by console the cursor content
        :param cursor:
        """
        for doc in cursor:
            print str(doc)

    def drop_collection(self):
        """
         drop the current collection
        """
        try:
            self.current_database.drop_collection(self.collection_name)
        except Exception, e:
            assert False, " ERROR - Deleting a collection %s in MongoDB...\n %s" % (self.current_collection, str(e))

    def drop_database(self):
        """
        remove the current database
        """
        try:
            __logger__.debug("database to delete: %s" % self.database_name)
            self.client.drop_database(self.database_name)
        except Exception, e:
            assert False, " ERROR - Deleting a database %s in MongoDB...\n %s" % (self.current_collection, str(e))

    def get_all_databases(self):
        """
        Get all databases in mongo
        :return: Database array found
        """
        arr_dbs = self.client.database_names()
        return arr_dbs

    def get_all_databases_with_prefix(self, l_prefix):
        """
        Get all databases that starts with the prefix
        :param l_prefix: Database prefix expected
        :return: array with databases found
        """
        l_dbs = []
        arr_dbs = self.client.database_names()
        for x_db in arr_dbs:
            for prefix in l_prefix:
                if x_db.startswith(prefix):
                    l_dbs.append(x_db)
        return l_dbs

    def match_prefix_with_list(x_db, l_prefix):
        """
        Check if the database starts with any prefix contained in the prefix list
        :param x_db: database name
        :param l_prefix:
        :return: True od False depends on if some prefix matches
        """
        for prefix in l_prefix:
            if x_db.startswith(prefix):
                return True
        return False

    def get_all_databases_without_prefix(self, l_prefix):
        """
        Get all databases that not start with the prefix
        :param l_prefix: Database prefix to exclude
        :return: array with databases found
        """
        l_dbs = []
        arr_dbs = self.client.database_names()
        for x_db in arr_dbs:
            if not self.match_prefix_with_list(x_db, l_prefix):
                l_dbs.append(x_db)
        return l_dbs

    def get_collections_by_db(self, name_db):
        """
        Get all collection in a mongo database
        :param name_db: Database to search
        :return: array with the collections
        """
        l_collections = []
        collections = self.client[name_db].collection_names()
        for collect in collections:
            l_collections.append(collect)
        return l_collections

    def get_all_documents_in_collection(self, db, collection, pattern={}):
        """
        Get all documents from the collection
        :param db: mongo database
        :param collection: collection database
        :param pattern: Search pattern -dict-
        :return: All documents in collection
        """
        l_items = []
        self.client[db].choice_collection(collection)
        items = self.find_with_retry(pattern)
        l_items = items
        return l_items

    def disconnect(self):
        """
        disconnect to mongo
        """
        try:
            self.client.close()
        except Exception, e:
             assert False, " ERROR - Disconnecting to MongoDB...\n %s\n%s " % (self.current_collection, str(e))

