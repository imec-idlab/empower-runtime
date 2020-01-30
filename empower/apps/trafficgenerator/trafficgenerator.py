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

""" Traffic Generator App
    Generates:
        - Iperf3 Traffic (UDP or TCP)
        - ICMP Traffic
    Keeps last data per LVAP for:
        - ICMP (Latency)
        - Bin Counter (Throughput)
    """

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_MONITORING_PERIOD

from empower.apps.trafficgenerator.parsers import icmp_output_parser

import json
import collections
import subprocess
import threading
import time


class TrafficGenerator(EmpowerApp):
    """Traffic Generator App

    Command Line Parameters:
        tenant_id: tenant id

        every: loop period in ms (optional, default 5000ms)

    External Parameters:
        lvap_traffic_descriptor: lvaps_traffic_config.json

        {
          "lvaps": {
            "00:00:00:AA:AA:AA": {
              "hostname": "hostname",
              "ip_addr": "127.0.0.1",
              "processes": {
                "icmp": {
                  "process": null,
                  "thread": null,
                  "last_data": null,
                  "active": false
                },
                "iperf3": {
                  "process": null,
                  "bandwidth": "20Mbps"
                  "protocol": "-u", # or blank in case TCP
                  "duration": 6000  # in seconds
                  "dst_port": "5001",
                  "active": false
                },
                "bin_counter": {
                  "last_data": null
                }
              }
            },
            ...
          }
        }

    Example:
        ./empower-runtime.py apps.trafficgenerator.trafficgenerator \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__config_file_path = self.config_file_path

        # Load traffic descriptor from JSON
        self.__lvap_traffic_descriptor = self.lvap_traffic_descriptor

    def loop(self):
        """Periodic job."""
        self.log.debug('Traffic Generator Loop...')

        # For each LVAP connected
        for lvap in self.lvaps():
            # If there is traffic to be generated for this LVAP
            if str(lvap.addr) in self.__lvap_traffic_descriptor:
                # For processes that need to be initialized
                if 'processes' in self.__lvap_traffic_descriptor[str(lvap.addr)]:
                    for process_name in self.__lvap_traffic_descriptor[str(lvap.addr)]['processes']:
                        if 'process' in self.__lvap_traffic_descriptor[str(lvap.addr)]['processes'][process_name]:
                            # If there is a process.Popen
                            if isinstance(self.__lvap_traffic_descriptor[str(lvap.addr)]['processes'][process_name]['process'],
                                          subprocess.Popen):
                                # If process is active
                                if self.__lvap_traffic_descriptor[str(lvap.addr)]['processes'][process_name]['process'].poll() \
                                        is not None:
                                    # Initialize LVAP process
                                    self.initialize_lvap_process(process_name, str(lvap.addr))
                            else:
                                # Initialize LVAP process
                                self.initialize_lvap_process(process_name, str(lvap.addr))

                        if 'bin_counter' in process_name:
                            # Get bin counter
                            bin_counter_data = self.bin_counter(lvap=lvap.addr).to_dict()
                            last_data = {}
                            if bin_counter_data['tx_bytes'] \
                                    and bin_counter_data['rx_bytes'] \
                                    and bin_counter_data['tx_bytes_per_second'] \
                                    and bin_counter_data['rx_bytes_per_second']:
                                last_data['timestamp'] = time.time()
                                last_data['tx_bytes'] = bin_counter_data['tx_bytes'][0]
                                last_data['rx_bytes'] = bin_counter_data['rx_bytes'][0]
                                last_data['tx_bytes_per_second'] = bin_counter_data['tx_bytes_per_second'][0]
                                last_data['rx_bytes_per_second'] = bin_counter_data['rx_bytes_per_second'][0]
                            self.__lvap_traffic_descriptor[str(lvap.addr)]['processes'][process_name]['last_data'] = \
                                last_data

    @property
    def config_file_path(self):
        """Return config_file_path"""

        return self.__config_file_path

    @config_file_path.setter
    def config_file_path(self, value):
        """Set config_file_path"""
        if isinstance(value, str):
            self.__config_file_path = value
        else:
            raise ValueError("Invalid value type for config_file_path, should be a string!")

    @property
    def lvap_traffic_descriptor(self):
        """Return default lvap_traffic_descriptor"""
        try:
            lvap_traffic_dict = \
                json.loads(open(self.__config_file_path).read())
            return lvap_traffic_dict
        except TypeError:
            raise ValueError("Invalid value for lvap_traffic_config or file does not exist!")

    @lvap_traffic_descriptor.setter
    def lvap_traffic_descriptor(self, value):
        """Set lvap_traffic_descriptor"""

        if value is not None:
            try:
                self.__lvap_traffic_descriptor = json.loads(open(value).read())
            except TypeError:
                raise ValueError("Invalid value for lvap_traffic_config or file does not exist!")
        else:
            self.__lvap_traffic_descriptor = None

    def initialize_lvap_process(self, process_name, lvap_addr):
        self.log.debug('Initialize LVAP Process: lvap: ' + str(lvap_addr) + ' process: ' + str(process_name))

        if process_name == 'icmp':
            # ICMP command
            icmp_terminal_command = ['ping', str(self.__lvap_traffic_descriptor[lvap_addr]['ip_addr'])]

            # Initialize ICMP
            self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['process'] = \
                subprocess.Popen(icmp_terminal_command, stdout=subprocess.PIPE)

            # Number of lines maintained
            number_of_lines = 1
            self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['last_data'] = \
                collections.deque(maxlen=number_of_lines)

            # Create thread for ICMP
            self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['thread'] = \
                threading.Thread(target=icmp_output_parser.read_icmp_output,
                                 args=(self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['process'],
                                       self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['last_data']
                                       .append))
            self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['thread'].daemon = True
            self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['thread'].start()

        # IPERF3 command
        elif process_name == 'iperf3':
            iperf3_terminal_command = ['iperf3',
                                       '-c', str(self.__lvap_traffic_descriptor[lvap_addr]['ip_addr']),
                                       str(self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['protocol']),
                                       '-b', str(self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['bandwidth']),
                                       '-t', str(self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['duration']),
                                       '-p', str(self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['dst_port'])]

            # Initialize IPERF3
            self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['process'] = \
                subprocess.Popen(iperf3_terminal_command, stdout=subprocess.PIPE)
            # No need for thread because uses bin_counter

        self.__lvap_traffic_descriptor[lvap_addr]['processes'][process_name]['active'] = True

    def to_dict(self):
        """ Return a JSON-serializable."""
        out = {}
        # Removing thread and process fields
        for lvap in self.__lvap_traffic_descriptor:
            out[lvap] = {}
            for field in self.__lvap_traffic_descriptor[lvap]:
                if field == 'processes':
                    out[lvap][field] = {}
                    for process_name in self.__lvap_traffic_descriptor[lvap][field]:
                        out[lvap][field][process_name] = {}
                        for data_field in self.__lvap_traffic_descriptor[lvap][field][process_name]:
                            # Not adding the non-serializable objects
                            if 'thread' not in data_field and 'process' not in data_field:
                                out[lvap][field][process_name][data_field] = self.__lvap_traffic_descriptor[lvap][field][process_name][data_field]
                else:
                    out[lvap][field] = self.__lvap_traffic_descriptor[lvap][field]
        return out


def launch(tenant_id, every=DEFAULT_MONITORING_PERIOD):
    """ Initialize the module. """

    return TrafficGenerator(tenant_id=tenant_id,
                            config_file_path="empower/apps/trafficgenerator/configs/lvaps_traffic_config_dev.json",
                            every=every)