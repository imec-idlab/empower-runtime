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

"""Sandbox MCDA handover manager APP."""

from empower.core.app import EmpowerApp
from empower.main import RUNTIME
from empower.core.resourcepool import BT_HT20

from skcriteria import Data, MIN, MAX
from skcriteria.madm import closeness, simple
import math
import time
import json

DEFAULT_LONG_PERIOD = 20000


class MCDAHandoverManager(EmpowerApp):
    """Sandbox MCDA handover manager APP.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.sandbox.managers.mcdahandovermanager.mcdahandovermanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__mcda_handover_manager = {"message": "Sandbox MCDA handover manager is online!", "wtps": {}}

        # Stats handlers
        self.__slice_stats_handler = None
        self.__wifi_stats_handler = None
        self.__ucqm_stats_handler = None
        self.__flow_handler = None
        self.__active = True
        self.__mcda_handover_manager['active'] = self.__active

        # MCDA file handlers
        self.__mcda_results_filename = 'empower/apps/sandbox/managers/mcdahandovermanager/results/mcda_run_.txt'
        self.__mcda_descriptor_filename = "empower/apps/sandbox/managers/mcdahandovermanager/descriptors/" + str(
            self.descriptor)

        # Other parameters
        self.__initial_association = True
        self.__db_monitor = self.db_monitor

        self.__mcda_descriptor = None
        self.__mcda_targets = None

        # Load MCDA descriptor from JSON
        try:
            with open(self.__mcda_descriptor_filename) as f:
                self.__mcda_descriptor = json.load(f)['params']['mcda_descriptor']
                self.load_targets()
        except TypeError:
            raise ValueError("Invalid value for input file or file does not exist!")

    def load_targets(self):
        self.__mcda_targets = []
        for target in self.__mcda_descriptor['targets']:
            if target == "MAX":
                self.__mcda_targets.append(MAX)
            else:
                self.__mcda_targets.append(MIN)

    def loop(self):
        """Periodic job."""
        if self.__mcda_descriptor is not None and self.__active:

            # Step 1: creating structure to handle all metrics
            self.create_mcda_structure()

            # Step 2: Update WTP/LVAP association map
            self.update_wtp_association_map()

            # Step 3: for each criteria, get all metrics and populate structure
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
                elif crr_criteria == 'wtp_load_expected_mbps':
                    self.initialize_wtp_load_expected()
                elif crr_criteria == 'sta_association_flag':
                    self.get_sta_association_flag()

            # Step 4: get all flows from flow manager APP
            if self.get_flow_handler():
                if self.__flow_handler['flows'] is not None:

                    # Step 5: Compute WTP expected load if present in the criteria
                    if 'wtp_load_expected_mbps' in self.__mcda_descriptor['criteria']:
                        self.compute_wtp_load_expected_mbps()

                    # Step 6: for each lvap in the network, get a decision using the TOPSIS method
                    for lvap in self.lvaps():
                        crr_lvap_addr = str(lvap.addr)

                        # Create MCDA structure
                        mtx = []
                        wtp_addresses = []
                        for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
                            wtp_addresses.append(crr_wtp_addr)
                            if crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                                mtx.append(
                                    self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics'][
                                        'values'])

                        # if any of the (active) flows in this LVAP is QoS, use QoS weights
                        # otherwise, stick with the BE weights
                        mcda_weights = self.__mcda_descriptor['weights_be']
                        if crr_lvap_addr in self.__flow_handler['lvap_flow_map']:
                            if any(i in self.__flow_handler['lvap_flow_map'][crr_lvap_addr] for i in self.__flow_handler['qos_flows']):
                                mcda_weights = self.__mcda_descriptor['weights_qos']


                        # Lists must have the same length
                        data = Data(mtx,
                                    self.__mcda_targets,
                                    weights=mcda_weights,
                                    anames=wtp_addresses,
                                    cnames=self.__mcda_descriptor['criteria'])

                        dm = closeness.TOPSIS()
                        dec = dm.decide(data)
                        best_alternative_wtp_addr = data.anames[dec.best_alternative_]

                        if self.__db_monitor:
                            for i in range(0, len(mtx)):
                                closeness_list = dec.e_.closeness.tolist()
                                ranks = dec.rank_.tolist()
                                closeness_res = closeness_list[i]
                                if math.isnan(closeness_res):
                                    closeness_res = None

                                fields = ['LVAP_ADDR', 'WTP_ADDR'] + \
                                         self.__mcda_descriptor['criteria'] + \
                                         ['RANK', 'CLOSENESS']

                                values = [crr_lvap_addr, wtp_addresses[i]] + mtx[i] + [ranks[i], closeness_res]
                                # Saving into db
                                self.monitor.insert_into_db(table='mcda_results', fields=fields, values=values)

                            # # TODO: Improve writing info...
                            # f = open(self.__mcda_results_filename, 'w+')
                            # f.write('Decision for LVAP: ' + crr_lvap_addr + '\n' + str(
                            #     dec) + '\nMove to WTP: ' + best_alternative_wtp_addr + '\n')
                            # f.close()

                        # Step 7: is handover needed? Do it and set the flag to 0 for all other blocks
                        # (this could be improved, but get block with given address should be implemented)
                        # Compute WTP expected load if present in the criteria
                        if 'sta_association_flag' in self.__mcda_descriptor['criteria']:
                            sta_association_index = self.__mcda_descriptor['criteria'].index('sta_association_flag')
                        old_wtp_addr = None
                        for block in self.blocks():
                            crr_wtp_addr = str(block.addr)
                            if lvap.blocks[0] is not None:
                                if crr_wtp_addr == best_alternative_wtp_addr:
                                    # Do handover to this block only if the station is not connected to it
                                    sta_crr_wtp_addr = str(lvap.blocks[0].addr)
                                    if sta_crr_wtp_addr != best_alternative_wtp_addr:
                                        self.log.info("Sandbox handover triggered!")
                                        old_wtp_addr = sta_crr_wtp_addr
                                        # Handover now..
                                        lvap.blocks = block
                                    # and update metrics
                                    if 'sta_association_flag' in self.__mcda_descriptor['criteria']:
                                        self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics'][
                                            'values'][sta_association_index] = 1
                                elif 'sta_association_flag' in self.__mcda_descriptor['criteria']:
                                    self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics'][
                                        'values'][sta_association_index] = 0

                        # Recalculate WTP expected load on handover, if any...
                        # OBS: not possible to access lvap.blocks[0] while performing handover
                        if 'wtp_load_expected_mbps' in self.__mcda_descriptor['criteria']:
                            if old_wtp_addr is not None:
                                self.recalculate_wtp_load_expected_mbps(old_wtp_addr=old_wtp_addr,
                                                                        best_alternative_wtp_addr=best_alternative_wtp_addr,
                                                                        moving_lvap_addr=crr_lvap_addr)

            # Start considering association and expected load from now on...
            if self.__initial_association:
                self.__initial_association = False

            if self.__db_monitor is not None:
                fields = self.__mcda_descriptor['criteria'] + ['TYPE']
                values = self.__mcda_descriptor['weights_qos'] + ['QoS']

                # Saving into db
                self.monitor.insert_into_db(table='mcda_weights', fields=fields, values=values)

                fields = self.__mcda_descriptor['criteria'] + ['TYPE']
                values = self.__mcda_descriptor['weights_be'] + ['BE']

                # Saving into db
                self.monitor.insert_into_db(table='mcda_weights', fields=fields, values=values)

                # Keeping only the last measurements in db
                self.monitor.keep_last_measurements_only('mcda_association_stats')
                self.monitor.keep_last_measurements_only('mcda_results')
                self.monitor.keep_last_measurements_only('mcda_weights')

    def recalculate_wtp_load_expected_mbps(self, old_wtp_addr, best_alternative_wtp_addr, moving_lvap_addr):
        wtp_load_expected_mbps_index = self.__mcda_descriptor['criteria'].index('wtp_load_expected_mbps')

        # Reduce expected load from old wtp (for each lvap structure)
        for crr_lvap_addr in self.__mcda_handover_manager['wtps'][old_wtp_addr]['lvaps']:
            # Meaning that the moving_lvap_addr is moving out...
            if moving_lvap_addr in self.__flow_handler['lvap_load_expected_map']:
                self.__mcda_handover_manager['wtps'][old_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                    wtp_load_expected_mbps_index] -= sum(self.__flow_handler['lvap_load_expected_map'][moving_lvap_addr])

        # Increase expected load from new wtp
        for crr_lvap_addr in self.__mcda_handover_manager['wtps'][best_alternative_wtp_addr]['lvaps']:
            # Meaning that the moving_lvap_addr is moving in...
            if moving_lvap_addr in self.__flow_handler['lvap_load_expected_map']:
                self.__mcda_handover_manager['wtps'][best_alternative_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                    wtp_load_expected_mbps_index] += sum(self.__flow_handler['lvap_load_expected_map'][moving_lvap_addr])

    def compute_wtp_load_expected_mbps(self):
        crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_load_expected_mbps')
        for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['expected_load'] = 0
            for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps']:
                if crr_lvap_addr in self.__flow_handler['lvap_load_expected_map']:
                    self.__mcda_handover_manager['wtps'][crr_wtp_addr]['expected_load'] += \
                    sum(self.__flow_handler['lvap_load_expected_map'][crr_lvap_addr])

        for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
            for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                discount_factor = 0
                if crr_lvap_addr in self.__flow_handler['lvap_load_expected_map']:
                    # Discounting this lvap expected load
                    if crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps']:
                        discount_factor = sum(self.__flow_handler['lvap_load_expected_map'][crr_lvap_addr])

                self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                    crr_criteria_index] = self.__mcda_handover_manager['wtps'][crr_wtp_addr]['expected_load'] - discount_factor

    def create_mcda_structure(self):
        for wtp in self.wtps():
            crr_wtp_addr = str(wtp.addr)
            if crr_wtp_addr not in self.__mcda_handover_manager['wtps']:

                # Initializing criteria with None
                self.__mcda_handover_manager['wtps'][crr_wtp_addr] = {'lvaps': {},
                                                             'connected_lvaps': [],
                                                             'expected_load': 0}
            for lvap in self.lvaps():
                crr_lvap_addr = str(lvap.addr)
                if crr_lvap_addr not in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                    self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr] = {
                        'metrics': {
                            'names': self.__mcda_descriptor['criteria'],
                            'values': [None] * len(self.__mcda_descriptor['criteria']),
                        }
                    }

    def get_flow_handler(self):
        # Flow Manager
        if 'empower.apps.sandbox.managers.flowmanager.flowmanager' in RUNTIME.tenants[self.tenant_id].components:
            self.__flow_handler = self.__flow_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.sandbox.managers.flowmanager.flowmanager'].to_dict()
            return True
        else:
            self.__flow_handler = None
            raise ValueError("APP 'empower.apps.sandbox.managers.flowmanager.flowmanager' is not online!")
            return False

    def get_wtp_load_measurements(self):
        # Slice stats handler
        if 'empower.apps.handlers.slicestatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__slice_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.slicestatshandler'].to_dict()
            crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_load_measured_mbps')
            for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
                if crr_wtp_addr in self.__slice_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                        wtp_mean_throughput_mbps = \
                            self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall']['throughput_mbps']['mean']
                        if wtp_mean_throughput_mbps is not None:
                            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
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
            for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
                if crr_wtp_addr in self.__slice_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                        wtp_mean_queue_delay_ms = \
                            self.__slice_stats_handler['wtps'][crr_wtp_addr]['overall']['queue_delay_ms']['mean']
                        if wtp_mean_queue_delay_ms is not None:
                            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
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
            for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
                if crr_wtp_addr in self.__wifi_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                        wtp_mean_channel_load_rate = \
                            self.__wifi_stats_handler['wtps'][crr_wtp_addr]['channel_utilization']['mean']
                        if wtp_mean_channel_load_rate is not None:
                            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
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
        if 'empower.apps.handlers.ucqmstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__ucqm_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.ucqmstatshandler'].to_dict()
            crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_sta_rssi_dbm')
            for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
                if crr_wtp_addr in self.__ucqm_stats_handler['wtps']:
                    for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                        if crr_lvap_addr in self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps']:
                            wtp_sta_mean_rssi_dbm = \
                                self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['mov_rssi'][
                                    'mean']
                            if wtp_sta_mean_rssi_dbm is not None:
                                self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                    crr_criteria_index] = wtp_sta_mean_rssi_dbm
                            else:
                                self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                    crr_criteria_index] = None
                        else:
                            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                crr_criteria_index] = None
                else:
                    raise ValueError("WTP is not yet present in ucqmstatshandler dictionary!")
                    return False
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.ucqmstatshandler' is not online!")
            return False

    def get_sta_association_flag(self):
        crr_criteria_index = self.__mcda_descriptor['criteria'].index('sta_association_flag')
        crr_time_in_ms = int(round(time.time()))
        for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
            for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                if not self.__initial_association:
                    if crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps']:
                        self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                            crr_criteria_index] = 1
                    else:
                        self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                            crr_criteria_index] = 0
                else:
                    self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                        crr_criteria_index] = 0

                if self.__db_monitor:

                    fields = ['LVAP_ADDR', 'WTP_ADDR', 'ASSOCIATION_FLAG']
                    values = [crr_lvap_addr,
                              crr_wtp_addr,
                              self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                                  crr_criteria_index]]

                    # Saving into db
                    self.monitor.insert_into_db(table='mcda_association_stats',
                                                fields=fields,
                                                values=values,
                                                crr_time_in_ms=crr_time_in_ms)

    def update_wtp_association_map(self):
        for lvap in self.lvaps():
            crr_lvap_addr = str(lvap.addr)
            if lvap.blocks[0] is not None:
                associated_wtp_addr = str(lvap.blocks[0].addr)
                for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
                    if crr_wtp_addr == associated_wtp_addr:
                        if crr_lvap_addr not in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps']:
                            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps'].append(crr_lvap_addr)
                    else:
                        if crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps']:
                            self.__mcda_handover_manager['wtps'][crr_wtp_addr]['connected_lvaps'].remove(crr_lvap_addr)

    def initialize_wtp_load_expected(self):
        crr_criteria_index = self.__mcda_descriptor['criteria'].index('wtp_load_expected_mbps')
        for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
            for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                    crr_criteria_index] = 0  # WTP expected load initialized with 0

    @property
    def mcda_descriptor(self):
        """Return default mcda_descriptor"""
        return self.__mcda_descriptor

    @mcda_descriptor.setter
    def mcda_descriptor(self, value):
        """Set mcda_descriptor"""
        self.__mcda_descriptor = value
        self.load_targets()

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
    def active(self):
        """Return active."""
        return self.__active

    @active.setter
    def active(self, value):
        """Set active."""
        self.__active = value

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
        self.__mcda_handover_manager['active'] = self.__active
        return self.__mcda_handover_manager


def launch(tenant_id,
           descriptor,
           db_monitor,
           every=DEFAULT_LONG_PERIOD):
    """ Initialize the module. """

    return MCDAHandoverManager(tenant_id=tenant_id,
                              descriptor=descriptor,
                              db_monitor=db_monitor,
                              every=every)
