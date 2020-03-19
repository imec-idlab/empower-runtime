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

"""Sandbox MCDA Manager APP."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.main import RUNTIME
from skcriteria import Data, MIN, MAX
from skcriteria.madm import closeness, simple
import json
import subprocess


class MCDAManager(EmpowerApp):
    """Sandbox MCDA Manager APP.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.sandbox.mcdamanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__mcda_manager = {"message": "Sandbox MCDA Manager is online!", "wtps": {}}
        self.__slice_stats_handler = None
        self.__wifi_stats_handler = None
        self.__ucqm_stats_handler = None
        self.__mcda_results_filename = 'empower/apps/sandbox/managers/results/mcda_run_.txt'


        # Load MCDA descriptor from JSON
        try:
            with open("empower/apps/sandbox/managers/descriptors/mcdainput.json") as f:
                self.__mcda_descriptor = json.load(f)
                self.__mcda_targets = []
                for target in self.__mcda_descriptor['targets']:
                    if target == "MAX":
                        self.__mcda_targets.append(MAX)
                    else:
                        self.__mcda_targets.append(MIN)
                # Creating mgen script and execute it
                for flow in self.__mcda_descriptor['flows']:
                    try:
                        multiplier = 1
                        # For the POISSON distribution 120 pps = 1Mbps
                        if flow['distribution'] == 'POISSON':
                            multiplier = 120
                        f = open('empower/apps/sandbox/managers/scripts/mgen/flow' + str(flow['id']) + '.mgn', 'w')
                        f.write('0.0 ON 1 ' + flow['protocol'] + ' DST ' + flow['dst_ip_addr'] + '/' + str(
                            flow['port']) + ' ' + flow['distribution'] + ' [' + str(
                            int(flow['req_throughput_mbps'] * multiplier)) + ' ' + str(flow['pkt_size']) + ']\n' + str(
                            flow['duration']) + ' OFF 1')
                        f.close()
                    except TypeError:
                        raise ValueError("Invalid path for mgen script files!")
        except TypeError:
            raise ValueError("Invalid value for input file or file does not exist!")
            self.__mcda_descriptor = None

    def loop(self):
        """Periodic job."""
        # self.log.debug("Sandbox MCDA Manager APP loop...")

        if self.__mcda_descriptor is not None:

            # Step 1: creating structure to handle all metrics
            for wtp in self.wtps():
                crr_wtp_addr = str(wtp.addr)
                if crr_wtp_addr not in self.__mcda_manager['wtps']:
                    # Initializing criteria with None
                    self.__mcda_manager['wtps'][crr_wtp_addr] = {'lvaps': {}, 'active_flows': {'QoS': [], 'BE': []}}
                    for lvap in self.lvaps():
                        crr_lvap_addr = str(lvap.addr)
                        if crr_lvap_addr not in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                            self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr] = {
                                'metrics': {
                                    'names': self.__mcda_descriptor['criteria'],
                                    'values': [None] * len(self.__mcda_descriptor['criteria']),
                                }
                            }

            # Step 2: for each criteria, get all metrics and populate structure
            for crr_criteria in self.__mcda_descriptor['criteria']:
                if crr_criteria == 'wtp_load_measured_mbps':
                    if not self.get_wtp_load_measurements():
                        return
                elif crr_criteria == 'wtp_queue_delay_ms':
                    if not self.get_wtp_queue_delay_measurements():
                        return
                elif crr_criteria == 'wtp_channel_load_rate':
                    if not self.get_wtp_channel_load_measurements():
                        return
                elif crr_criteria == 'wtp_sta_rssi_dbm':
                    if not self.get_lvap_rssi_measurements():
                        return
                elif crr_criteria == 'sta_association_flag':
                    self.get_sta_association_flag()
                elif crr_criteria == 'wtp_load_expected_mbps':
                    self.initialize_wtp_expected_load()

            # Step 3: one by one, get the first flow and the other flows towards the same destination
            if len(self.__mcda_descriptor['flows']) > 0:
                # Assuming that flows are already sorted (priority flows first)
                crr_flow = self.__mcda_descriptor['flows'][0]
                active_flows_list = [crr_flow]
                wtp_load_expected_mbps = self.__mcda_descriptor['flows'][0]['req_throughput_mbps']
                self.__mcda_descriptor['flows'].pop(0)

                # Step 4: searching for flows towards the same destination
                for flow in self.__mcda_descriptor['flows']:
                    if crr_flow['lvap_addr'] == flow['lvap_addr']:
                        wtp_load_expected_mbps += flow['req_throughput_mbps']
                        active_flows_list.append(flow)
                        self.__mcda_descriptor['flows'].pop(self.__mcda_descriptor['flows'].index(flow))

                # Step 5: for each flow, or set of flows to allocate, get a decision using the TOPSIS method
                mtx = []
                wtp_addresses = []
                for crr_wtp_addr in self.__mcda_manager['wtps']:
                    wtp_addresses.append(crr_wtp_addr)
                    if crr_flow['lvap_addr'] in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                        mtx.append(self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_flow['lvap_addr']]['metrics'][
                                       'values'])

                # List must have the same length
                data = Data(mtx,
                            self.__mcda_targets,
                            weights=self.__mcda_descriptor['weights'],
                            anames=wtp_addresses,
                            cnames=self.__mcda_descriptor['criteria'])

                dm = closeness.TOPSIS()
                dec = dm.decide(data)
                f = open(self.__mcda_results_filename, 'w+')
                f.write(str(dec) + '\n')
                f.close()
                best_alternative_wtp_addr = data.anames[dec.best_alternative_]

                # Step 6: is handover needed? Do it so and then set the flag to 0 for all the other blocks
                # (this could be improved, but get block with given address should be implemented)
                sta_association_index = self.__mcda_descriptor['criteria'].index('sta_association_flag')
                for block in self.blocks():
                    crr_wtp_addr = str(block.addr)
                    if crr_wtp_addr == best_alternative_wtp_addr:
                        # Do handover
                        for lvap in self.lvaps():
                            # If there is a static placement for the station
                            if str(lvap.addr) == crr_flow['lvap_addr']:
                                # If the station is not connected to it already
                                if str(lvap.blocks[0].addr) != str(block.addr):
                                    self.log.info("Sandbox handover triggered!")
                                    lvap.blocks = block
                        # and update metrics
                        self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_flow['lvap_addr']]['metrics']['values'][
                            sta_association_index] = 1
                    else:
                        self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_flow['lvap_addr']]['metrics']['values'][
                            sta_association_index] = 0

                # Step 7: allocate flow, updating metrics
                wtp_load_expected_mbps_index = self.__mcda_descriptor['criteria'].index('wtp_load_expected_mbps')
                for lvap in self.lvaps():
                    crr_lvap_addr = str(lvap.addr)
                    self.__mcda_manager['wtps'][best_alternative_wtp_addr]['lvaps'][crr_lvap_addr]['metrics'][
                        'values'][wtp_load_expected_mbps_index] += wtp_load_expected_mbps

                # TODO Step (feature): recalculate expected load for the WTPs (expire inactive flows)

                # Step 8: Run flows with mgen
                mgen_command = ['mgen', 'input',
                                'empower/apps/sandbox/managers/scripts/mgen/flow' + str(crr_flow['id']) + '.mgn']
                subprocess.Popen(mgen_command)

                # Fill in active flows TODO: check this list on wifislicemanager APP!
                for flow in active_flows_list:
                    self.__mcda_manager['wtps'][best_alternative_wtp_addr]['active_flows'][flow['type']].append(flow)

    def get_wtp_load_measurements(self):
        # Slice stats handler
        if 'empower.apps.handlers.slicestatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__slice_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.slicestatshandler'].to_dict()
            crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_load_measured_mbps')
            for crr_wtp_addr in self.__mcda_manager['wtps']:
                if crr_wtp_addr in self.__slice_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                        wtp_mean_throughput_mbps = \
                            self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall']['throughput_mbps']['mean']
                        if wtp_mean_throughput_mbps is not None:
                            self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                crr_criteria_index] = wtp_mean_throughput_mbps
                        else:
                            raise ValueError("WTP average throughput is not ready yet!")
                            return False
                else:
                    raise ValueError("WTP is not yet present in slicestatshandler dictionary!")
                    return False
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.slicestatshandler' is not online!")
            return False

    def get_wtp_queue_delay_measurements(self):
        # Slice stats handler
        if 'empower.apps.handlers.slicestatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__slice_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.slicestatshandler'].to_dict()
            crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_queue_delay_ms')
            for crr_wtp_addr in self.__mcda_manager['wtps']:
                if crr_wtp_addr in self.__slice_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                        wtp_mean_queue_delay_ms = \
                            self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall']['queue_delay_ms']['mean']
                        if wtp_mean_queue_delay_ms is not None:
                            self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                crr_criteria_index] = wtp_mean_queue_delay_ms
                        else:
                            raise ValueError("WTP average queue_delay is not ready yet!")
                            return False
                else:
                    raise ValueError("WTP is not yet present in slicestatshandler dictionary!")
                    return False
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.slicestatshandler' is not online!")
            return False

    def get_wtp_channel_load_measurements(self):
        # WiFi stats handler
        if 'empower.apps.handlers.wifistatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__wifi_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.wifistatshandler'].to_dict()
            crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_channel_load_rate')
            for crr_wtp_addr in self.__mcda_manager['wtps']:
                if crr_wtp_addr in self.__wifi_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                        wtp_mean_channel_load_rate = \
                            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['mean']
                        if wtp_mean_channel_load_rate is not None:
                            self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                crr_criteria_index] = wtp_mean_channel_load_rate
                        else:
                            raise ValueError("WTP channel load rate is not ready yet!")
                            return False
                else:
                    raise ValueError("WTP is not yet present in wifistatshandler dictionary!")
                    return False
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.wifistatshandler' is not online!")
            return False

    def get_lvap_rssi_measurements(self):
        # UCQM stats handler
        worst_case_rssi = -100  # add this in case no LVAP yet
        if 'empower.apps.handlers.ucqmstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__ucqm_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.ucqmstatshandler'].to_dict()
            crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_sta_rssi_dbm')
            for crr_wtp_addr in self.__mcda_manager['wtps']:
                if crr_wtp_addr in self.__ucqm_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                        if crr_lvap_addr in self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps']:
                            wtp_sta_median_rssi_dbm = \
                                self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['mov_rssi'][
                                    'median']
                            if wtp_sta_median_rssi_dbm is not None:
                                self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                    crr_criteria_index] = wtp_sta_median_rssi_dbm
                            else:
                                self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                    crr_criteria_index] = worst_case_rssi
                        else:
                            self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                crr_criteria_index] = worst_case_rssi
                else:
                    raise ValueError("WTP is not yet present in wifistatshandler dictionary!")
                    return False
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.wifistatshandler' is not online!")
            return False

    def get_sta_association_flag(self):
        crr_criteria_index = self.__mcda_descriptor['criteria'].index('sta_association_flag')
        for lvap in self.lvaps():
            crr_lvap_addr = str(lvap.addr)
            associated_wtp_addr = str(lvap.blocks[0].addr)
            for crr_wtp_addr in self.__ucqm_stats_handler['wtps']:
                if crr_wtp_addr == associated_wtp_addr:
                    self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                        crr_criteria_index] = 1
                else:
                    self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                        crr_criteria_index] = 0

    def initialize_wtp_expected_load(self):
        crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_load_expected_mbps')
        for crr_wtp_addr in self.__ucqm_stats_handler['wtps']:
            for crr_lvap_addr in self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps']:
                if self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][crr_criteria_index] is None:
                    self.__mcda_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][crr_criteria_index] = 0  # WTP expected load initialized with 0

    @property
    def mcda_descriptor(self):
        """Return default mcda_descriptor"""
        return self.__mcda_descriptor

    @mcda_descriptor.setter
    def mcda_descriptor(self, value):
        """Set mcda_descriptor"""
        self.__mcda_descriptor = value

    @property
    def mcda_targets(self):
        """Return default mcda_targets"""
        return self.__mcda_targets

    @mcda_targets.setter
    def mcda_targets(self, value):
        """Set mcda_targets"""
        self.__mcda_targets = value

    @property
    def slice_stats_handler(self):
        """Return default slice_stats_handler"""
        return self.__slice_stats_handler

    @slice_stats_handler.setter
    def slice_stats_handler(self, value):
        """Set slice_stats_handler"""
        self.__slice_stats_handler = value

    @property
    def wifi_stats_handler(self):
        """Return default wifi_stats_handler"""
        return self.__wifi_stats_handler

    @wifi_stats_handler.setter
    def wifi_stats_handler(self, value):
        """Set wifi_stats_handler"""
        self.__wifi_stats_handler = value

    @property
    def ucqm_stats_handler(self):
        """Return default ucqm_stats_handler"""
        return self.__ucqm_stats_handler

    @ucqm_stats_handler.setter
    def ucqm_stats_handler(self, value):
        """Set ucqm_stats_handler"""
        self.__ucqm_stats_handler = value

    @property
    def every(self):
        """Return loop period."""
        return self.__every

    @every.setter
    def every(self, value):
        """Set loop period."""
        self.log.info("Setting control loop interval to %ums", int(value))
        self.__every = int(value)
        super().restart(self.__every)

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__mcda_manager


def launch(tenant_id,
           every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return MCDAManager(tenant_id=tenant_id,
                       every=every)
