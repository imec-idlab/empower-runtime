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

"""Slice Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
import psycopg2
import time
import statistics


class WiFiStatsHandler(EmpowerApp):
    """WiFi Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.wifitatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__db_user = self.db_user
        self.__db_pass = self.db_pass
        self.__wifi_stats_handler = {"message": "WiFi stats handler is online!", "wtps": {}}

    def wtp_up(self, wtp):
        for block in wtp.supports:
            # Calling WiFi stats
            self.wifi_stats(block=block,
                            every=DEFAULT_PERIOD,
                            callback=self.wifi_stats_callback)

    def loop(self):
        """Periodic job."""
        self.log.debug('WiFi Stats Handler APP Loop...')
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
                sql_delete_query = """DELETE FROM wifi_stats WHERE TIMESTAMP_MS < %s"""
                cursor.execute(sql_delete_query, (int(round(
                    time.time() - 5 * 60)),))  # Keeping only the last measurements (i.e., only the last 5 minutes)
                connection.commit()

            except (Exception, psycopg2.Error) as error:
                if (connection):
                    self.log.debug('WiFi stats failed to delete records from wifi_stats table!')
            finally:
                # closing database connection.
                if (connection):
                    cursor.close()
                    connection.close()

    def wifi_stats_callback(self, wifi_stats):
        """ New stats available. """
        crr_wtp_addr = str(wifi_stats.block.addr)
        if crr_wtp_addr is not None:
            if crr_wtp_addr not in self.__wifi_stats_handler['wtps']:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr] = {
                    "tx_per_second": None,
                    "rx_per_second": None,
                    "channel": None,
                    "channel_utilization": {
                        "values": [],
                        "mean": None,
                        "median": None,
                        "stdev": None
                    }
                }

            # TX and RX metrics
            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['tx_per_second'] = wifi_stats.tx_per_second
            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['rx_per_second'] = wifi_stats.rx_per_second

            # Channel is not going to change at runtime
            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel'] = wifi_stats.block.channel

            # Channel utilization moving window
            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'].append(
                wifi_stats.tx_per_second + wifi_stats.rx_per_second)

            if len(self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values']) > 10:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'].pop(0)

            if len(self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values']) > 2:
                # Mean
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization'][
                    'mean'] = statistics.mean(
                    self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'])

                # Median
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization'][
                    'median'] = statistics.median(
                    self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'])

                # STDEV
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization'][
                    'stdev'] = statistics.stdev(
                    self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'])

            if self.__db_monitor is not None:
                if self.__db_user is not None and self.__db_pass is not None:
                    crr_time_in_ms = int(round(time.time()))
                    try:
                        connection = psycopg2.connect(user=self.__db_user,
                                                      password=self.__db_pass,
                                                      host="127.0.0.1",
                                                      port="5432",
                                                      database="empower")
                        cursor = connection.cursor()

                        postgres_insert_query = """ INSERT INTO wifi_stats (ADDRESS, TX, RX, CHANNEL, CHANNEL_UTILIZATION, TIMESTAMP_MS) VALUES (%s,%s,%s,%s,%s,%s)"""
                        record_to_insert = (
                            str(crr_wtp_addr),
                            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['TX'],
                            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['RX'],
                            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel'],
                            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization'],
                            crr_time_in_ms)
                        cursor.execute(postgres_insert_query, record_to_insert)
                        connection.commit()
                        count = cursor.rowcount

                    except (Exception, psycopg2.Error) as error:
                        if (connection):
                            self.log.debug('WiFi stats failed to insert record into wifi_stats table!')
                    finally:
                        # closing database connection.
                        if (connection):
                            cursor.close()
                        connection.close()

    @property
    def wifi_stats_handler(self):
        """Return default wifi_stats_handler"""
        return self.__wifi_stats_handler

    @wifi_stats_handler.setter
    def wifi_stats_handler(self, value):
        """Set wifi_stats_handler"""
        self.__wifi_stats_handler = value

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
        return self.__wifi_stats_handler


def launch(tenant_id, db_monitor=None, db_user=None, db_pass=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return WiFiStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, db_user=db_user, db_pass=db_pass, every=every)
