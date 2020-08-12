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
from empower.core.app import DEFAULT_MONITORING_PERIOD
from empower.core.app import DEFAULT_PERIOD
import statistics


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
        self.__raw_metrics = ['rx_bytes',
                              'rx_packets',
                              'tx_bytes',
                              'tx_packets']
        self.__moving_window_metrics = ['tx_throughput_mbps', 'rx_throughput_mbps']
        self.__bin_stats_handler = {'message': 'Bin stats handler is online!', 'lvaps': {}}

    def loop(self):
        """Periodic job."""
        for lvap in self.lvaps():
            # Calling bin counter for each LVAP
            self.bin_counter(lvap=lvap.addr,
                             every=DEFAULT_MONITORING_PERIOD,
                             callback=self.bin_stats_callback)
        if self.__db_monitor is not None:
            self.monitor.keep_last_measurements_only(table='bin_stats')

    def bin_stats_callback(self, bin_stats):
        """ New stats available. """
        lvap_addr = str(bin_stats.to_dict()['lvap'])
        if lvap_addr not in self.__bin_stats_handler['lvaps']:
            self.__bin_stats_handler['lvaps'][lvap_addr] = {
                'bin_stats': bin_stats.to_dict(),
                'tx_throughput_mbps': {
                    "values": [],
                    "mean": None,
                    "median": None,
                    "stdev": None
                },
                'rx_throughput_mbps': {
                    "values": [],
                    "mean": None,
                    "median": None,
                    "stdev": None
                }
            }
        else:
            self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats'] = bin_stats.to_dict()

        for metric in self.__raw_metrics:
            self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats'][metric + '_moving'] = []

        if self.__db_monitor is not None:

            rx_bytes = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['rx_bytes'][0]
            rx_packets = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['rx_packets'][0]
            tx_bytes = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['tx_bytes'][0]
            tx_packets = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['tx_packets'][0]

            # bytes per second
            if not self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['rx_bytes_per_second']:
                rx_bytes_per_second = 0  # as None
            else:
                rx_bytes_per_second = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['rx_bytes_per_second'][0]

            # packets per second
            if not self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['rx_packets_per_second']:
                rx_packets_per_second = 0  # as None
            else:
                rx_packets_per_second = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['rx_packets_per_second'][0]

            if not self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['tx_bytes_per_second']:
                tx_bytes_per_second = 0  # as None
            else:
                tx_bytes_per_second = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['tx_bytes_per_second'][0]

            if not self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['tx_packets_per_second']:
                tx_packets_per_second = 0  # as None
            else:
                tx_packets_per_second = self.__bin_stats_handler['lvaps'][lvap_addr]['bin_stats']['tx_packets_per_second'][0]

            if tx_bytes_per_second == 0:
                tx_throughput_mbps = 0
            else:
                tx_throughput_mbps = tx_bytes_per_second / 125000

            if rx_bytes_per_second == 0:
                rx_throughput_mbps = 0
            else:
                rx_throughput_mbps = rx_bytes_per_second / 125000

            self.__bin_stats_handler['lvaps'][lvap_addr]['tx_throughput_mbps']['values'].append(tx_throughput_mbps)
            self.__bin_stats_handler['lvaps'][lvap_addr]['rx_throughput_mbps']['values'].append(rx_throughput_mbps)

            for metric in self.__moving_window_metrics:
                if len(self.__bin_stats_handler['lvaps'][lvap_addr][metric]['values']) > 10:
                    self.__bin_stats_handler['lvaps'][lvap_addr][metric]['values'].pop(0)

                if len(self.__bin_stats_handler['lvaps'][lvap_addr][metric]['values']) >= 2:
                    # Mean
                    self.__bin_stats_handler['lvaps'][lvap_addr][metric]['mean'] = statistics.mean(
                        self.__bin_stats_handler['lvaps'][lvap_addr][metric]['values'])

                    # Median
                    self.__bin_stats_handler['lvaps'][lvap_addr][metric]['median'] = statistics.median(
                        self.__bin_stats_handler['lvaps'][lvap_addr][metric]['values'])

                    # STDEV
                    self.__bin_stats_handler['lvaps'][lvap_addr][metric]['stdev'] = statistics.stdev(
                        self.__bin_stats_handler['lvaps'][lvap_addr][metric]['values'])

            fields = ['LVAP_ADDR',
                      'RX_BYTES', 'RX_BYTES_PER_SECOND', 'RX_PACKETS', 'RX_PACKETS_PER_SECOND',
                      'TX_BYTES', 'TX_BYTES_PER_SECOND', 'TX_PACKETS', 'TX_PACKETS_PER_SECOND',
                      'TX_THROUGHPUT_MBPS', 'RX_THROUGHPUT_MBPS']

            values = [str(bin_stats.to_dict()['lvap']),
                      rx_bytes, rx_bytes_per_second, rx_packets, rx_packets_per_second,
                      tx_bytes, tx_bytes_per_second, tx_packets, tx_packets_per_second,
                      tx_throughput_mbps, rx_throughput_mbps]

            # Saving into db
            self.monitor.insert_into_db(table='bin_stats', fields=fields, values=values)

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
    def bin_stats_handler(self):
        """Return default bin_stats_handler"""
        return self.__bin_stats_handler

    @bin_stats_handler.setter
    def bin_stats_handler(self, value):
        """Set bin_stats_handler"""
        self.__bin_stats_handler = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__bin_stats_handler


def launch(tenant_id, db_monitor=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return BinStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, every=every)
