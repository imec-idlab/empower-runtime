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
from empower.core.app import DEFAULT_MONITORING_PERIOD
from empower.core.app import DEFAULT_PERIOD
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
        self.__wifi_stats_handler = {"message": "WiFi stats handler is online!", "wtps": {}}

    def wtp_up(self, wtp):
        for block in wtp.supports:
            # Calling WiFi stats
            self.wifi_stats(block=block,
                            every=DEFAULT_MONITORING_PERIOD,
                            callback=self.wifi_stats_callback)

    def loop(self):
        """Periodic job."""
        # self.log.debug('WiFi Stats Handler APP Loop...')
        if self.__db_monitor is not None:
            self.monitor.keep_last_measurements_only(table='wifi_stats')

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
            if wifi_stats.tx_per_second > 0:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['tx_per_second'] = wifi_stats.tx_per_second / 125000  # to Mbps
            else:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['tx_per_second'] = wifi_stats.tx_per_second

            if wifi_stats.rx_per_second > 0:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['rx_per_second'] = wifi_stats.rx_per_second / 125000  # to Mbps
            else:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['rx_per_second'] = wifi_stats.rx_per_second

            # Channel is not going to change at runtime
            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel'] = wifi_stats.block.channel

            # Channel utilization moving window
            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'].append(
                wifi_stats.tx_per_second + wifi_stats.rx_per_second)

            if len(self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values']) > 10:
                self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values'].pop(0)

            if len(self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['values']) >= 2:
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
                fields = ['WTP_ADDR', 'TX', 'RX', 'CHANNEL', 'CHANNEL_UTILIZATION']
                values = [str(crr_wtp_addr),
                          self.__wifi_stats_handler['wtps'][crr_wtp_addr]['tx_per_second'],
                          self.__wifi_stats_handler['wtps'][crr_wtp_addr]['rx_per_second'],
                          self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel'],
                          (self.__wifi_stats_handler['wtps'][crr_wtp_addr]['tx_per_second'] + self.__wifi_stats_handler['wtps'][crr_wtp_addr]['rx_per_second'])]

                # Saving into db
                self.monitor.insert_into_db(table='wifi_stats', fields=fields, values=values)

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

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__wifi_stats_handler


def launch(tenant_id, db_monitor=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return WiFiStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, every=every)
