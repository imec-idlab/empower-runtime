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

"""NCQM Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_MONITORING_PERIOD
from empower.core.app import DEFAULT_PERIOD
import psycopg2
import time


class NCQMStatsHandler(EmpowerApp):
    """NCQM Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.ncqmstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__db_user = self.db_user
        self.__db_pass = self.db_pass
        self.__ncqm_stats_handler = {'message': 'NCQM stats handler is online!'}

    def wtp_up(self, wtp):
        for block in wtp.supports:
            # Calling NCQM stats
            self.ncqm(block=block,
                      every=DEFAULT_MONITORING_PERIOD,
                      callback=self.ncqm_stats_callback)

    def loop(self):
        """Periodic job."""
        # self.log.debug('NCQM Stats Handler APP Loop...')
        if self.__db_monitor is not None:
            self.keep_last_measurements_only()

    def keep_last_measurements_only(self):
        if self.__db_user is not None and self.__db_pass is not None:
            try:
                connection = psycopg2.connect(user=self.__db_user,
                                              password=self.__db_pass,
                                              host="127.0.0.1",
                                              port="5432",
                                              database="empower")
                cursor = connection.cursor()
                sql_delete_query = """DELETE FROM ncqm_stats WHERE TIMESTAMP_MS < %s"""
                cursor.execute(sql_delete_query, (int(round(
                    time.time() - 10 * 60)),))  # Keeping only the last measurements (i.e., only the last 10 minutes)
                connection.commit()

            except (Exception, psycopg2.Error) as error:
                if (connection):
                    self.log.debug('NCQM stats failed to delete records from ncqm_stats table!')
            finally:
                # closing database connection.
                if (connection):
                    cursor.close()
                    connection.close()

    def ncqm_stats_callback(self, ncqm_stats):
        """ New stats available. """
        crr_wtp_addr = str(ncqm_stats.block.addr)
        if crr_wtp_addr is not None:
            if self.__db_monitor is not None:
                if self.__db_user is not None and self.__db_pass is not None:
                    crr_time_in_ms = int(round(time.time()))
                    ncqm = ncqm_stats.block.ncqm
                    for unknown_ap in ncqm:
                        try:
                            connection = psycopg2.connect(user=self.__db_user,
                                                          password=self.__db_pass,
                                                          host="127.0.0.1",
                                                          port="5432",
                                                          database="empower")
                            cursor = connection.cursor()

                            postgres_insert_query = """ INSERT INTO ncqm_stats (ADDRESS, HIST_PACKETS, LAST_PACKETS, LAST_RSSI_AVG, LAST_RSSI_STD, MOV_RSSI, UNKNOWN_AP, WTP_AP, TIMESTAMP_MS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                            record_to_insert = (
                                crr_wtp_addr,
                                ncqm[unknown_ap]['hist_packets'],
                                ncqm[unknown_ap]['last_packets'],
                                ncqm[unknown_ap]['last_rssi_avg'],
                                ncqm[unknown_ap]['last_rssi_std'],
                                ncqm[unknown_ap]['mov_rssi'],
                                str(unknown_ap),
                                "WTP: " + str(crr_wtp_addr) + " - Unknown AP: " + str(unknown_ap),
                                crr_time_in_ms)
                            cursor.execute(postgres_insert_query, record_to_insert)
                            connection.commit()
                            count = cursor.rowcount

                        except (Exception, psycopg2.Error) as error:
                            if (connection):
                                self.log.debug('NCQM stats failed to insert record into ncqm_stats table!')
                        finally:
                            # closing database connection.
                            if (connection):
                                cursor.close()
                                connection.close()

    @property
    def ncqm_stats_handler(self):
        """Return default ncqm_stats_handler"""
        return self.__ncqm_stats_handler

    @ncqm_stats_handler.setter
    def ncqm_stats_handler(self, value):
        """Set ncqm_stats_handler"""
        self.__ncqm_stats_handler = value

    @property
    def db_monitor(self):
        """Return db_monitor"""
        return self.__db_monitor

    @db_monitor.setter
    def db_monitor(self, value):
        """Set db_monitor"""
        if value is not None:
            self.__db_monitor = value

    @property
    def db_user(self):
        """Return db_user"""
        return self.__db_user

    @db_user.setter
    def db_user(self, value):
        """Set db_user"""
        if value is not None:
            self.__db_user = value

    @property
    def db_pass(self):
        """Return db_pass"""
        return self.__db_pass

    @db_pass.setter
    def db_pass(self, value):
        """Set db_pass"""
        if value is not None:
            self.__db_pass = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__ncqm_stats_handler


def launch(tenant_id, db_monitor=None, db_user=None, db_pass=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return NCQMStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, db_user=db_user, db_pass=db_pass, every=every)
