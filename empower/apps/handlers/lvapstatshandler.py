#!/usr/bin/env python3
#
# Copyright (c) 2019 Pedro Heleno Isolani
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

"""LVAP Stats Handler App"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_MONITORING_PERIOD
from empower.main import RUNTIME

import statistics
import time


class LVAPStatsHandler(EmpowerApp):
    """LVAP Stats Handler App

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.lvapstatshandler.lvapstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__max_measurements = 10  # 100
        self.__lvap_stats_handler = {}
        self.__experiment_latency_file = open("experiment_latency.txt", "w")
        self.__experiment_throughput_file = open("experiment_throughput.txt", "w")
        self.__experiment_throughput_2_file = open("experiment_throughput_2.txt", "w")


        self.__experiment_latency_file.write(
            "Timestamp, Average Latency (ms), Median Latency (ms), Stdev Latency (ms)\n")
        self.__experiment_throughput_file.write(
            "Timestamp, Average Throughput (ms), Median Throughput (ms), Stdev Throughput (ms)\n")
        self.__experiment_throughput_2_file.write(
            "Timestamp, Average Throughput (ms), Median Throughput (ms), Stdev Throughput (ms)\n")

    def loop(self):
        """Periodic job."""
        self.log.debug('LVAP Stats Handler APP Loop...')
        if 'empower.apps.trafficgenerator.trafficgenerator' in RUNTIME.tenants[self.tenant_id].components:
            self.handle_lvap_stats(
                RUNTIME.tenants[self.tenant_id].components['empower.apps.trafficgenerator.trafficgenerator'].to_dict())



    @property
    def lvap_stats_handler(self):
        """Return default lvap_stats_handler"""
        return self.__lvap_stats_handler

    @lvap_stats_handler.setter
    def lvap_stats_handler(self, value):
        """Set lvap_stats_handler"""
        self.__lvap_stats_handler = value

    @property
    def max_measurements(self):
        """Return default max_measurements"""
        return self.__max_measurements

    @max_measurements.setter
    def max_measurements(self, value):
        """Set max_measurements"""
        self.__max_measurements = value

    def handle_lvap_stats(self, data):
        crr_time = time.time()
        for lvap in data:
            if lvap not in self.__lvap_stats_handler:
                self.__lvap_stats_handler[lvap] = \
                    {"metrics":
                         {"latency": {"timestamps": [], "values": [], "loss_timestamps": [], "unit": "ms",
                                      "mean": None, "median": None, "stdev": None},
                          "throughput": {"timestamps": [],
                                         "tx_mbits": {"values": [],
                                                      "mean": None, "median": None, "stdev": None},
                                         "rx_mbits": {"values": [],
                                                      "mean": None, "median": None, "stdev": None},
                                         "tx_mbits_per_second": {"values": [],
                                                                 "mean": None, "median": None, "stdev": None},
                                         "rx_mbits_per_second": {"values": [],
                                                                 "mean": None, "median": None, "stdev": None}
                                         }
                          }
                     }
            if 'processes' in data[lvap]:
                for process_name in data[lvap]['processes']:
                    # Process ICMP Stats
                    if 'icmp' in process_name:
                        # If there is ICMP data
                        if 'last_data' in data[lvap]['processes'][process_name]:

                            # Keeping only the last max_measurements
                            if len(self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps']) + \
                                    len(self.__lvap_stats_handler[lvap]['metrics']['latency']['loss_timestamps']) > \
                                    self.max_measurements:

                                # If empty packet timestamps
                                if not len(self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps']):
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['loss_timestamps'].pop(0)
                                # If empty lost packet timestamps
                                elif not len(self.__lvap_stats_handler[lvap]['metrics']['latency']['loss_timestamps']):
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps'].pop(0)
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['values'].pop(0)
                                # If lost packets are too old so pop it from the results
                                elif min(self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps']) > min(
                                        self.__lvap_stats_handler[lvap]['metrics']['latency']['loss_timestamps']):
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['loss_timestamps'].pop(0)
                                else:
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps'].pop(0)
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['values'].pop(0)

                            # Add timestamp
                            if data[lvap]['processes'][process_name]['last_data']:
                                if len(data[lvap]['processes'][process_name]['last_data']):
                                    # If not timeout..
                                    if data[lvap]['processes'][process_name]['last_data'][0]['value'] is not None:
                                        self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps'].\
                                            append(data[lvap]['processes'][process_name]['last_data'][0]['timestamp'])
                                        # Add current latency (Assuming it always gathers in (ms))
                                        if data[lvap]['processes'][process_name]['last_data'][0]['unit'] == "ms":
                                            self.__lvap_stats_handler[lvap]['metrics']['latency']['values']. \
                                                append(data[lvap]['processes'][process_name]['last_data'][0]['value'])
                                    else:
                                        self.__lvap_stats_handler[lvap]['metrics']['latency']['loss_timestamps']. \
                                            append(data[lvap]['processes'][process_name]['last_data'][0]['timestamp'])

                            # Computing mean, median, std, and so on...
                            if len(self.__lvap_stats_handler[lvap]['metrics']['latency']['timestamps']) > 1:
                                self.__lvap_stats_handler[lvap]['metrics']['latency']['mean'] = statistics.mean(
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['values'])
                                self.__lvap_stats_handler[lvap]['metrics']['latency']['median'] = statistics.median(
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['values'])
                                self.__lvap_stats_handler[lvap]['metrics']['latency']['stdev'] = statistics.stdev(
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['values'])
                            else:
                                self.__lvap_stats_handler[lvap]['metrics']['latency']['mean'] = None
                                self.__lvap_stats_handler[lvap]['metrics']['latency']['median'] = None
                                self.__lvap_stats_handler[lvap]['metrics']['latency']['stdev'] = None

                            # Fill experiment file
                            self.__experiment_latency_file.write(
                                str(crr_time) + "," +
                                str(self.__lvap_stats_handler[lvap]['metrics']['latency']['mean']) + "," +
                                str(self.__lvap_stats_handler[lvap]['metrics']['latency']['median']) + "," + str(
                                    self.__lvap_stats_handler[lvap]['metrics']['latency']['stdev']) + "\n")

                    # Process Bin Counter Stats
                    elif 'bin_counter' in process_name:
                        # If there is TX or RX data
                        if 'last_data' in data[lvap]['processes'][process_name]:

                            # Keeping only the last max_measurements
                            if len(self.__lvap_stats_handler[lvap]['metrics']['throughput']['timestamps']) > \
                                    self.max_measurements:
                                for field in self.__lvap_stats_handler[lvap]['metrics']['throughput']:
                                    if 'timestamps' in field:
                                        self.__lvap_stats_handler[lvap]['metrics']['throughput'][field].pop(0)
                                    else:
                                        self.__lvap_stats_handler[lvap]['metrics']['throughput'][field]['values'].pop(0)
                            # If there is data
                            if data[lvap]['processes'][process_name]['last_data']:
                                # If the data is complete
                                if data[lvap]['processes'][process_name]['last_data']['timestamp'] \
                                        and data[lvap]['processes'][process_name]['last_data']['tx_bytes'] \
                                        and data[lvap]['processes'][process_name]['last_data']['rx_bytes']\
                                        and data[lvap]['processes'][process_name]['last_data']['tx_bytes_per_second']\
                                        and data[lvap]['processes'][process_name]['last_data']['rx_bytes_per_second']:

                                    # Timestamp
                                    self.__lvap_stats_handler[lvap]['metrics']['throughput']['timestamps']. \
                                            append(data[lvap]['processes'][process_name]['last_data']['timestamp'])
                                    # TX Bytes
                                    self.__lvap_stats_handler[lvap]['metrics']['throughput']['tx_mbits']['values']. \
                                        append(data[lvap]['processes'][process_name]['last_data'][
                                                   'tx_bytes'] / 125000)  # In Mbits
                                    # RX Bytes
                                    self.__lvap_stats_handler[lvap]['metrics']['throughput']['rx_mbits']['values']. \
                                        append(data[lvap]['processes'][process_name]['last_data'][
                                                   'rx_bytes'] / 125000)  # In Mbits
                                    # TX Bytes per second
                                    self.__lvap_stats_handler[lvap]['metrics']['throughput']['tx_mbits_per_second'][
                                        'values'].append(data[lvap]['processes'][process_name]['last_data'][
                                                   'tx_bytes_per_second'] / 125000)  # In Mbps
                                    # RX Bytes per second
                                    self.__lvap_stats_handler[lvap]['metrics']['throughput']['rx_mbits_per_second'][
                                        'values'].append(data[lvap]['processes'][process_name]['last_data'][
                                                   'rx_bytes_per_second'] / 125000)  # In Mbps

                                    # Computing mean, median, std, and so on...
                                    if len(self.__lvap_stats_handler[lvap]['metrics']['throughput']['timestamps']) > 1:
                                        # TX Bytes
                                        for field in self.__lvap_stats_handler[lvap]['metrics']['throughput']:
                                            if 'timestamps' not in field:
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                    'mean'] = statistics.mean(
                                                    self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                        'values'])
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                    'median'] = statistics.median(
                                                    self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                        'values'])
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                    'stdev'] = statistics.stdev(
                                                    self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                        'values'])
                                    else:
                                        for field in self.__lvap_stats_handler[lvap]['metrics']['throughput']:
                                            if 'timestamps' not in field:
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                    'mean'] = None
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                    'median'] = None
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][field][
                                                    'stdev'] = None

                                    # Fill in the experiment file
                                    if lvap == "28:37:37:24:A7:F2":
                                        self.__experiment_throughput_file.write(
                                            str(crr_time) + "," +
                                            str(self.__lvap_stats_handler[lvap]['metrics']['throughput']['tx_mbits_per_second'][
                                                    'mean']) + "," +
                                            str(self.__lvap_stats_handler[lvap]['metrics']['throughput']['tx_mbits_per_second'][
                                                    'median']) + "," + str(
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput']['tx_mbits_per_second'][
                                                    'stdev']) + "\n")
                                    else:
                                        self.__experiment_throughput_2_file.write(
                                            str(crr_time) + "," +
                                            str(self.__lvap_stats_handler[lvap]['metrics']['throughput'][
                                                    'tx_mbits_per_second'][
                                                    'mean']) + "," +
                                            str(self.__lvap_stats_handler[lvap]['metrics']['throughput'][
                                                    'tx_mbits_per_second'][
                                                    'median']) + "," + str(
                                                self.__lvap_stats_handler[lvap]['metrics']['throughput'][
                                                    'tx_mbits_per_second'][
                                                    'stdev']) + "\n")



    def to_dict(self):
        """ Return a JSON-serializable."""
        out = self.__lvap_stats_handler
        return out


def launch(tenant_id, every=DEFAULT_MONITORING_PERIOD):
    """ Initialize the module. """

    return LVAPStatsHandler(tenant_id=tenant_id, every=every)