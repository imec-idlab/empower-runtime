#!/usr/bin/env python3
#
# Copyright (c) 2020 Pedro Heleno Isolani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

import configparser
import psycopg2
import time


class EmpowerMon:
    """
    EmpowerMon base class used for monitoring data using PostgreSQL
    * contains common CRUD functions
    """

    def __init__(self):
        self.__db_user = None
        self.__db_pass = None
        self.__db_name = None
        self.__db_port = None
        self.__db_host = None
        self.__threshold_min = 5

        self.__config = configparser.ConfigParser()
        self.__config.read('empower/grafana/config.ini')

        if 'PostgreSQL' in self.__config:
            db_config = self.__config['PostgreSQL']
            params = ['db_host', 'db_port', 'db_name', 'db_user', 'db_pass']
            if all(param in db_config for param in params):
                if all(param is not None for param in db_config):
                    self.__db_user = db_config['db_user']
                    self.__db_pass = db_config['db_pass']
                    self.__db_name = db_config['db_name']
                    self.__db_port = db_config['db_port']
                    self.__db_host = db_config['db_host']

            if 'threshold_min' in db_config:
                self.__threshold_min = db_config['threshold_min']

    def keep_last_measurements_only(self, table=None):
        try:
            connection = psycopg2.connect(user=self.__db_user,
                                          password=self.__db_pass,
                                          host=self.__db_host,
                                          port=self.__db_port,
                                          database="empower")
            cursor = connection.cursor()
            sql_delete_query = 'DELETE FROM ' + str(table) + ' WHERE TIMESTAMP_MS < %s'

            # Keeping only the last measurements (i.e., the last x minutes)
            cursor.execute(sql_delete_query, (int(round(time.time() - int(self.__threshold_min) * 60)),))
            connection.commit()

        except (Exception, psycopg2.Error) as error:
            if (connection):
                raise ValueError('EmpowerMon could not delete from ' + str(table) + ' with PostgreSQL!')
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()

    def insert_into_db(self, table, fields, values, crr_time_in_ms=None):
        if isinstance(fields, list) and isinstance(values, list):
            if crr_time_in_ms is None:
                crr_time_in_ms = int(round(time.time()))
            if fields and values and len(fields) == len(values):
                fields.append('TIMESTAMP_MS')
                values.append(crr_time_in_ms)
                fields_str = ','.join(map(str, fields))
                values_str = ','.join(['%s'] * len(values))
                postgres_insert_query = 'INSERT INTO ' + str(table) + ' (' + fields_str + ') VALUES (' + values_str + ')'
                try:
                    connection = psycopg2.connect(user=self.__db_user,
                                                  password=self.__db_pass,
                                                  host=self.__db_host,
                                                  port=self.__db_port,
                                                  database=self.__db_name)
                    cursor = connection.cursor()
                    cursor.execute(postgres_insert_query, values)
                    connection.commit()
                except (Exception, psycopg2.Error) as error:
                    if (connection):
                        raise ValueError('EmpowerMon could not insert into table: ' + str(table) + ' with PostgreSQL!')
                finally:
                    # closing database connection.
                    if (connection):
                        cursor.close()
                        connection.close()
            else:
                raise ValueError(
                    'EmpowerMon could not insert into table: ' + str(table) + ', fields and values not valid!')
        else:
            raise ValueError(
                'EmpowerMon could not insert into table: ' + str(table) + ', fields and values must be a list!')

