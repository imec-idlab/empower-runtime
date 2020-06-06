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
from empower.datatypes.dscp import DSCP
from empower.datatypes.etheraddress import EtherAddress
import statistics


class SliceStatsHandler(EmpowerApp):
    """Slice Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.slicestatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__slice_stats_handler = {"message": "Slice stats handler is online!", "wtps": {}}
        self.__tx_metrics = ['tx_bytes', 'tx_packets']
        self.__raw_metrics = ['deficit_used', 'deficit_avg', 'deficit', 'max_queue_length', 'crr_queue_length']
        self.__moving_window_metrics = ['queue_delay_ms', 'throughput_mbps']

    def loop(self):
        """Periodic job."""
        for wtp in self.wtps():
            for block in wtp.supports:
                for slice_dscp in self.tenant.slices:
                    # Calling slice stats for each slice DSCP
                    self.slice_stats(block=block,
                                     dscp=slice_dscp,
                                     every=DEFAULT_MONITORING_PERIOD,
                                     callback=self.slice_stats_callback)
        if self.__db_monitor is not None:
            self.monitor.keep_last_measurements_only('slice_stats')

    def slice_stats_callback(self, slice_stats):
        """ New stats available. """
        crr_wtp_addr = str(slice_stats.block.addr)
        crr_dscp = str(slice_stats.dscp)

        if crr_wtp_addr not in self.__slice_stats_handler['wtps']:
            self.__slice_stats_handler['wtps'][crr_wtp_addr] = {'slices': {}, 'overall': {
                'queue_delay_ms': {
                    "values": [],
                    "mean": None,
                    "median": None,
                    "stdev": None
                },
                'throughput_mbps': {
                    "values": [],
                    "mean": None,
                    "median": None,
                    "stdev": None
                }
            }}

        if crr_dscp not in self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices']:
            self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp] = {
                'tx_bytes': 0,
                'tx_packets': 0,
                'throughput_mbps': {
                    "values": [],
                    "mean": None,
                    "median": None,
                    "stdev": None
                },
                'deficit_used': None,
                'deficit_avg': None,
                'deficit': None,
                'queue_delay_ms': {
                    "values": [],
                    "mean": None,
                    "median": None,
                    "stdev": None
                },
                'max_queue_length': None,
                'crr_queue_length': None,
                'tx_bytes_moving': [],
                'tx_packets_moving': []
            }

        # Computing TX metrics...
        for metric in self.__tx_metrics:
            self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                metric + '_moving'].append(
                slice_stats.to_dict()['slice_stats'][metric])

            if len(self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                       metric + '_moving']) >= 2:
                # Calculate diff
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric] = \
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                        metric + '_moving'][1] - \
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                        metric + '_moving'][0]

                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                    metric + '_moving'].pop(0)

        # Computing TX megabits
        crr_tx_megabits = self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                              'tx_bytes'] / 125000  # from bytes to megabits

        # Computing throughput metric...
        crr_throughput_mbps = 0
        if self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['tx_bytes'] > 0:
            crr_throughput_mbps = self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][
                                      'tx_bytes'] / 1000 / 1000 * 8  # from bytes to Mbps
        self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['throughput_mbps']['values'].append(
            crr_throughput_mbps)

        crr_queue_delay_ms = 0
        if self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['tx_bytes'] > 0:
            crr_queue_delay_ms = slice_stats.to_dict()['slice_stats']['queue_delay'] / 1000  # from usec to ms
        self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['queue_delay_ms']['values'].append(
            crr_queue_delay_ms)

        for metric in self.__moving_window_metrics:
            if len(self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric]['values']) > 10:
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric]['values'].pop(0)

            if len(self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric]['values']) >= 2:
                # Mean
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric][
                    'mean'] = statistics.mean(
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric]['values'])

                # Median
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric][
                    'median'] = statistics.median(
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric]['values'])

                # STDEV
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric][
                    'stdev'] = statistics.stdev(
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric]['values'])

        # Computing queue delay metric...
        for metric in self.__raw_metrics:
            if self.slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['tx_bytes'] == 0:
                self.slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric] = 0
            else:
                self.slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp][metric] = \
                slice_stats.to_dict()['slice_stats'][metric]

        # Update wtp counters
        self.update_wtp_overall_counters(crr_wtp_addr=crr_wtp_addr)

        # Saving slice stats into db
        if self.__db_monitor is not None:

            # If there is a specific slice configuration for this WTP
            if EtherAddress(crr_wtp_addr) in self.tenant.slices[DSCP(crr_dscp)].wifi['wtps']:
                crr_quantum = self.tenant.slices[DSCP(crr_dscp)].wifi['wtps'][EtherAddress(crr_wtp_addr)]['static-properties']['quantum']
            else:
                crr_quantum = self.tenant.slices[DSCP(crr_dscp)].wifi['static-properties']['quantum']

            fields = ['WTP_ADDR', 'DSCP', 'WTP_DSCP',
                      'DEFICIT', 'DEFICIT_AVG', 'DEFICIT_USED',
                      'MAX_QUEUE_LENGTH', 'CRR_QUEUE_LENGTH',
                      'CURRENT_QUANTUM', 'QUEUE_DELAY_MSEC',
                      'TX_BYTES', 'TX_PACKETS', 'TX_MBITS', 'THROUGHPUT_MBPS']
            values = [str(crr_wtp_addr), str(crr_dscp), 'WTP: ' + str(crr_wtp_addr) + ' - Slice: ' + str(crr_dscp),
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['deficit'],
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['deficit_avg'],
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['deficit_used'],
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['max_queue_length'],
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['crr_queue_length'],
                    crr_quantum,
                    crr_queue_delay_ms,
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['tx_bytes'],
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][crr_dscp]['tx_packets'],
                    crr_tx_megabits,
                    crr_throughput_mbps]

            # Saving into db
            self.monitor.insert_into_db(table='slice_stats', fields=fields, values=values)

    def update_wtp_overall_counters(self, crr_wtp_addr):
        wtp_queue_delay_ms_overall = 0
        wtp_throughput_mbps_overall = 0
        for dscp in self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices']:
            wtp_queue_delay_ms_overall += \
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][dscp]['queue_delay_ms']['values'][-1]
            wtp_throughput_mbps_overall += \
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][dscp]['throughput_mbps']['values'][-1]

        self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall']['queue_delay_ms']['values'].append(
            wtp_queue_delay_ms_overall)
        self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall']['throughput_mbps']['values'].append(
            wtp_throughput_mbps_overall)

        for metric in self.__moving_window_metrics:
            if len(self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['values']) > 10:
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['values'].pop(0)

            if len(self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['values']) >= 2:
                # Mean
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['mean'] = statistics.mean(
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['values'])

                # Median
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['median'] = statistics.median(
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['values'])

                # STDEV
                self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['stdev'] = statistics.stdev(
                    self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall'][metric]['values'])

    @property
    def slice_stats_handler(self):
        """Return default slice_stats_handler"""
        return self.__slice_stats_handler

    @slice_stats_handler.setter
    def slice_stats_handler(self, value):
        """Set slice_stats_handler"""
        self.__slice_stats_handler = value

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
        return self.__slice_stats_handler


def launch(tenant_id, db_monitor=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return SliceStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, every=every)
