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

"""Bin Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
import psycopg2
import time


class BinStatsHandler(EmpowerApp):
    """Bin Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.binstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__db_user = self.db_user
        self.__db_pass = self.db_pass
        self.__raw_metrics = ['rx_bytes',
                              'rx_packets',
                              'tx_bytes',
                              'tx_packets']
        self.__bin_stats_handler = {'lvaps': {}}

    def loop(self):
        """Periodic job."""
        self.log.debug('Bin Stats Handler APP Loop...')
        for lvap in self.lvaps():
            # Calling bin counter for each LVAP
            self.bin_counter(lvap=lvap.addr,
                             callback=self.bin_stats_callback)
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
                sql_delete_query = """DELETE FROM bin_stats WHERE TIMESTAMP_MS < %s"""
                cursor.execute(sql_delete_query, (int(round(time.time() - 5 * 60)),))  # Keeping only the last measurements (i.e., only the last 5 minutes)
                connection.commit()

            except (Exception, psycopg2.Error) as error:
                if (connection):
                    self.log.debug('Bin stats failed to delete records from bin_stats table!')
            finally:
                # closing database connection.
                if (connection):
                    cursor.close()
                    connection.close()

    def bin_stats_callback(self, bin_stats):
        """ New stats available. """
        lvap = str(bin_stats.to_dict()['lvap'])
        self.__bin_stats_handler['lvaps'][lvap] = bin_stats.to_dict()

        for metric in self.__raw_metrics:
            self.__bin_stats_handler['lvaps'][lvap][metric + '_moving'] = []

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

                    rx_bytes = self.__bin_stats_handler['lvaps'][lvap]['rx_bytes'][0]
                    rx_packets = self.__bin_stats_handler['lvaps'][lvap]['rx_packets'][0]
                    tx_bytes = self.__bin_stats_handler['lvaps'][lvap]['tx_bytes'][0]
                    tx_packets = self.__bin_stats_handler['lvaps'][lvap]['tx_packets'][0]

                    # bytes per second
                    if not self.__bin_stats_handler['lvaps'][lvap]['rx_bytes_per_second']:
                        rx_bytes_per_second = 0     # as None
                    else:
                        rx_bytes_per_second = self.__bin_stats_handler['lvaps'][lvap]['rx_bytes_per_second'][0]

                    # packets per second
                    if not self.__bin_stats_handler['lvaps'][lvap]['rx_packets_per_second']:
                        rx_packets_per_second = 0     # as None
                    else:
                        rx_packets_per_second = self.__bin_stats_handler['lvaps'][lvap]['rx_packets_per_second'][0]

                    if not self.__bin_stats_handler['lvaps'][lvap]['tx_bytes_per_second']:
                        tx_bytes_per_second = 0     # as None
                    else:
                        tx_bytes_per_second = self.__bin_stats_handler['lvaps'][lvap]['tx_bytes_per_second'][0]

                    if not self.__bin_stats_handler['lvaps'][lvap]['tx_packets_per_second']:
                        tx_packets_per_second = 0     # as None
                    else:
                        tx_packets_per_second = self.__bin_stats_handler['lvaps'][lvap]['tx_packets_per_second'][0]

                    tx_throughput_mbps = tx_bytes_per_second / 125000
                    rx_throughput_mbps = rx_bytes_per_second / 125000

                    postgres_insert_query = """ INSERT INTO bin_stats (LVAP, RX_BYTES, RX_BYTES_PER_SECOND, RX_PACKETS, RX_PACKETS_PER_SECOND, TX_BYTES, TX_BYTES_PER_SECOND, TX_PACKETS, TX_PACKETS_PER_SECOND, TX_THROUGHPUT_MBPS, RX_THROUGHPUT_MBPS, TIMESTAMP_MS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    record_to_insert = (
                        str(bin_stats.to_dict()['lvap']),
                        rx_bytes,
                        rx_bytes_per_second,
                        rx_packets,
                        rx_packets_per_second,
                        tx_bytes,
                        tx_bytes_per_second,
                        tx_packets,
                        tx_packets_per_second,
                        tx_throughput_mbps,
                        rx_throughput_mbps,
                        crr_time_in_ms)
                    cursor.execute(postgres_insert_query, record_to_insert)
                    connection.commit()
                    count = cursor.rowcount

                except (Exception, psycopg2.Error) as error:
                    if (connection):
                        self.log.debug('Bin stats failed to insert record into bin_stats table!')
                finally:
                    # closing database connection.
                    if (connection):
                        cursor.close()
                        connection.close()

    @property
    def bin_stats_handler(self):
        """Return default bin_stats_handler"""
        return self.__bin_stats_handler

    @bin_stats_handler.setter
    def bin_stats_handler(self, value):
        """Set bin_stats_handler"""
        self.__bin_stats_handler = value

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
        return self.__bin_stats_handler


def launch(tenant_id, db_monitor=None, db_user=None, db_pass=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return BinStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, db_user=db_user, db_pass=db_pass, every=every)