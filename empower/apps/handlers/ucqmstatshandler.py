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

"""UCQM Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.datatypes.etheraddress import EtherAddress
import psycopg2
import time
import statistics


class UCQMStatsHandler(EmpowerApp):
    """UCQM Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.ucqmstatshandler\
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__db_user = self.db_user
        self.__db_pass = self.db_pass
        self.__ucqm_stats_handler = {"message": "UCQM stats handler is online!", "wtps": {}}

    def wtp_up(self, wtp):
        for block in wtp.supports:
            # Calling UCQM stats
            self.ucqm(block=block,
                      every=DEFAULT_PERIOD,
                      callback=self.ucqm_stats_callback)

    def loop(self):
        """Periodic job."""
        # self.log.debug('UCQM Stats Handler APP Loop...')
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
                sql_delete_query = """DELETE FROM ucqm_stats WHERE TIMESTAMP_MS < %s"""
                cursor.execute(sql_delete_query, (int(round(
                    time.time() - 10 * 60)),))  # Keeping only the last measurements (i.e., only the last 10 minutes)
                connection.commit()

            except (Exception, psycopg2.Error) as error:
                if (connection):
                    self.log.debug('UCQM stats failed to delete records from ucqm_stats table!')
            finally:
                # closing database connection.
                if (connection):
                    cursor.close()
                    connection.close()

    def ucqm_stats_callback(self, ucqm_stats):
        """ New stats available. """
        crr_wtp_addr = str(ucqm_stats.block.addr)
        if crr_wtp_addr is not None:
            if crr_wtp_addr not in self.__ucqm_stats_handler['wtps']:
                self.__ucqm_stats_handler['wtps'][crr_wtp_addr] = {'lvaps': {}}

            ucqm = ucqm_stats.block.ucqm
            for sta in ucqm:
                if self.lvap(EtherAddress(sta)) is not None:
                    # This is a station of this tenant
                    if str(sta) not in self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps']:
                        self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)] = {
                            'hist_packets': None,
                            'last_packets': None,
                            'mov_rssi': {
                                "values": [],
                                "mean": None,
                                "median": None,
                                "stdev": None
                            }}

                    # Hist and Last packets
                    self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                        'hist_packets'] = ucqm[sta]['hist_packets']
                    self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                        'last_packets'] = ucqm[sta]['last_packets']

                    # RSSI moving window (last_rssi_avg and last_rssi_std not used here)
                    self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)]['mov_rssi'][
                        'values'].append(ucqm[sta]['mov_rssi'])

                    if len(self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                               'mov_rssi']['values']) > 10:
                        self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                            'mov_rssi']['values'].pop(0)

                    if len(self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                               'mov_rssi']['values']) >= 2:
                        # Mean
                        self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                            'mov_rssi']['mean'] = statistics.mean(
                            self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                                'mov_rssi']['values'])
                        # Median
                        self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                            'mov_rssi']['median'] = statistics.median(
                            self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                                'mov_rssi']['values'])

                        # STDEV
                        self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                            'mov_rssi']['stdev'] = statistics.stdev(
                            self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][str(sta)][
                                'mov_rssi']['values'])

            if self.__db_monitor is not None:
                if self.__db_user is not None and self.__db_pass is not None:
                    crr_time_in_ms = int(round(time.time()))
                    for sta in ucqm:
                        try:
                            connection = psycopg2.connect(user=self.__db_user,
                                                          password=self.__db_pass,
                                                          host="127.0.0.1",
                                                          port="5432",
                                                          database="empower")
                            cursor = connection.cursor()

                            postgres_insert_query = """ INSERT INTO ucqm_stats (ADDRESS, STATION, HIST_PACKETS, LAST_PACKETS, LAST_RSSI_AVG, LAST_RSSI_STD, MOV_RSSI, WTP_STA, TIMESTAMP_MS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                            record_to_insert = (
                                str(crr_wtp_addr),
                                str(sta),
                                ucqm[sta]['hist_packets'],
                                ucqm[sta]['last_packets'],
                                ucqm[sta]['last_rssi_avg'],
                                ucqm[sta]['last_rssi_std'],
                                ucqm[sta]['mov_rssi'],
                                "WTP: " + str(crr_wtp_addr) + " - STA: " + str(sta),
                                crr_time_in_ms)
                            cursor.execute(postgres_insert_query, record_to_insert)
                            connection.commit()
                            count = cursor.rowcount

                        except (Exception, psycopg2.Error) as error:
                            if (connection):
                                self.log.debug('UCQM stats failed to insert record into ucqm_stats table!')
                        finally:
                            # closing database connection.
                            if (connection):
                                cursor.close()
                                connection.close()

    @property
    def ucqm_stats_handler(self):
        """Return default ucqm_stats_handler"""
        return self.__ucqm_stats_handler

    @ucqm_stats_handler.setter
    def ucqm_stats_handler(self, value):
        """Set ucqm_stats_handler"""
        self.__ucqm_stats_handler = value

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
        return self.__ucqm_stats_handler


def launch(tenant_id, db_monitor=None, db_user=None, db_pass=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return UCQMStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, db_user=db_user, db_pass=db_pass, every=every)
