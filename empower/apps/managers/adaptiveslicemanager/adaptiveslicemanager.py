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

"""Adaptive Slice Manager App."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.datatypes.dscp import DSCP
from empower.main import RUNTIME
from empower.apps.managers.adaptiveslicemanager.parsers import sliceconfigrequest


class AdaptiveSliceManager(EmpowerApp):
    """Adaptive Slice Manager App

    Command Line Parameters:
        tenant_id: tenant id
        minimum_quantum: minimum_quantum,
        maximum_quantum: maximum_quantum,
        quantum_decrease_rate: quantum_decrease_rate,
        quantum_increase_rate: quantum_increase_rate,
        db_monitor: db_monitor,
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.managers.adaptiveslicemanager.adaptiveslicemanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            --minimum_quantum=10
            --minimum_quantum=12000
            --quantum_increase_rate=0.1
            --quantum_decrease_rate=0.1
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__adaptive_slice_manager = {"message": "Adaptive Slice Manager is online!"}
        self.__lvap_stats_handler = None
        self.__slice_stats_handler = None
        self.__active_flows_handler = None
        self.__active = True
        self.__adaptive_slice_manager['active'] = self.__active
        self.__minimum_quantum = self.minimum_quantum
        self.__maximum_quantum = self.maximum_quantum
        self.__quantum_decrease_rate = self.quantum_decrease_rate
        self.__quantum_increase_rate = self.quantum_increase_rate
        self.__uplink_bw_threshold = self.__uplink_bw_threshold

    def loop(self):
        """Periodic job."""
        if self.__active:
            if self.get_slice_stats() and self.get_active_flows() and self.get_sta_stats():
                # Run only when there are QoS flows
                if self.__active_flows_handler['qos_flows']:
                    for crr_wtp_addr in self.__slice_stats_handler['wtps']:
                        if self.requirements_met(wtp=crr_wtp_addr):
                            factor = self.__quantum_increase_rate
                        else:
                            factor = self.__quantum_decrease_rate

                        # Reconfigure all slices in the WTP
                        self.reconfigure(factor, crr_wtp_addr)
                else:
                    for crr_wtp_addr in self.__slice_stats_handler['wtps']:
                        # Reconfigure all slices in the WTP
                        self.reset_all(crr_wtp_addr)

            if self.__db_monitor is not None:
                fields = ['MIN_QUANTUM', 'MAX_QUANTUM', 'INC_RATE', 'DEC_RATE', 'UP_BW_THRESHOLD_MBPS']
                values = [self.__minimum_quantum, self.__maximum_quantum,
                          self.__quantum_increase_rate, self.__quantum_decrease_rate, self.__uplink_bw_threshold]

                # Saving into db
                self.monitor.insert_into_db(table='adaptive_slicing', fields=fields, values=values)

                # Keeping only the last measurements in db
                self.monitor.keep_last_measurements_only('adaptive_slicing')

    def reset_all(self, crr_wtp_addr):
        for dscp in self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices']:
            current_quantum = self.tenant.slices[DSCP(dscp)].wifi['static-properties']['quantum']
            if self.__maximum_quantum != current_quantum:
                self.send_slice_config_to_wtp(dscp=dscp,
                                              new_quantum=self.__maximum_quantum)

    def reconfigure(self, factor, crr_wtp_addr):
        for be_dscp in self.__active_flows_handler['be_slices']:
            if be_dscp in self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices']:
                slice = self.__slice_stats_handler['wtps'][crr_wtp_addr]['slices'][be_dscp]
                # only if the slice active...
                if slice['tx_bytes'] > 0:
                    current_quantum = self.tenant.slices[DSCP(be_dscp)].wifi['static-properties']['quantum']
                    adapted_quantum = int(current_quantum * factor)
                    if adapted_quantum > self.__maximum_quantum:
                        adapted_quantum = self.__maximum_quantum
                    if adapted_quantum < self.__minimum_quantum:
                        adapted_quantum = self.__minimum_quantum
                    if adapted_quantum != current_quantum:
                        self.send_slice_config_to_wtp(dscp=be_dscp,
                                                      new_quantum=adapted_quantum)

    def requirements_met(self, wtp):
        for qos_flow_id in self.__active_flows_handler['qos_flows']:
            qos_flow = self.__active_flows_handler['flows'][qos_flow_id]
            # If downlink QoS flow
            if qos_flow['flow_dscp'] in self.__slice_stats_handler['wtps'][wtp]['slices']:
                queue_delay_median = \
                self.__slice_stats_handler['wtps'][wtp]['slices'][qos_flow['flow_dscp']]['queue_delay_ms']['median']
                if queue_delay_median is not None and qos_flow['flow_delay_req_ms'] is not None:
                    if qos_flow['flow_delay_req_ms'] < queue_delay_median:
                        return False
            # If uplink QoS flow
            elif qos_flow['flow_dscp'] is None:
                if 'flow_src_mac_addr' in qos_flow:
                    if qos_flow['flow_src_mac_addr'] in self.lvap_stats_handler['lvaps']:
                        sta_rx_bw_mean = \
                        self.lvap_stats_handler['lvaps'][qos_flow['flow_src_mac_addr']]['rx_throughput_mbps']['mean']
                        if sta_rx_bw_mean is not None:
                            # Applying bw threshold...
                            if sta_rx_bw_mean < (qos_flow['flow_bw_req_mbps'] * (1 - self.__uplink_bw_threshold)):
                                # Search if the LVAP is connected to the WTP being analyzed
                                for lvap in self.lvaps():
                                    if str(lvap.addr) == qos_flow['flow_src_mac_addr']:
                                        if str(lvap.blocks[0].addr) == wtp:
                                            return False
        return True

    def send_slice_config_to_wtp(self, dscp, new_quantum):
        new_slice = sliceconfigrequest.format_slice_config_request(tenant_id=self.tenant_id,
                                                                   dscp=dscp,
                                                                   default_quantum=new_quantum)
        self.log.debug("Sending new slice configurations to APs")
        self.tenant.set_slice(DSCP(dscp), new_slice)

    def get_active_flows(self):
        if 'empower.apps.managers.flowmanager.flowmanager' in RUNTIME.tenants[self.tenant_id].components:
            self.__active_flows_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.managers.flowmanager.flowmanager'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.managers.flowmanager.flowmanager' is not online!")
            return False

    def get_slice_stats(self):
        if 'empower.apps.handlers.slicestatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__slice_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.slicestatshandler'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.slicestatshandler' is not online!")
            return False

    def get_sta_stats(self):
        if 'empower.apps.handlers.binstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__lvap_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.binstatshandler'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.binstatshandler' is not online!")
            return False

    @property
    def active_flows_handler(self):
        """Return default active_flows_handler"""
        return self.__active_flows_handler

    @active_flows_handler.setter
    def active_flows_handler(self, value):
        """Set active_flows_handler"""
        self.__active_flows_handler = value

    @property
    def lvap_stats_handler(self):
        """Return default lvap_stats_handler"""
        return self.__lvap_stats_handler

    @lvap_stats_handler.setter
    def lvap_stats_handler(self, value):
        """Set lvap_stats_handler"""
        self.__lvap_stats_handler = value

    @property
    def slice_stats_handler(self):
        """Return default slice_stats_handler"""
        return self.__slice_stats_handler

    @slice_stats_handler.setter
    def slice_stats_handler(self, value):
        """Set slice_stats_handler"""
        self.__slice_stats_handler = value

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
    def adaptive_slice_manager(self):
        """Return default Adaptive Slice Manager"""
        return self.__adaptive_slice_manager

    @adaptive_slice_manager.setter
    def adaptive_slice_manager(self, value):
        """Set Adaptive Slice Manager"""
        self.__adaptive_slice_manager = value

    @property
    def minimum_quantum(self):
        """Return minimum quantum"""
        return self.__minimum_quantum

    @minimum_quantum.setter
    def minimum_quantum(self, value):
        """Set minimum_quantum"""
        if value is not None:
            try:
                self.__minimum_quantum = int(value)
            except TypeError:
                raise ValueError("Invalid value type for minimum_quantum, should be an integer!")
        else:
            self.__minimum_quantum = None

    @property
    def maximum_quantum(self):
        """Return maximum quantum"""
        return self.__maximum_quantum

    @maximum_quantum.setter
    def maximum_quantum(self, value):
        """Set maximum_quantum"""
        if value is not None:
            try:
                self.__maximum_quantum = int(value)
            except TypeError:
                raise ValueError("Invalid value type for maximum_quantum, should be an integer!")
        else:
            self.__maximum_quantum = 12000

    @property
    def quantum_decrease_rate(self):
        """Return quantum_decrease_rate"""
        return self.__quantum_decrease_rate

    @quantum_decrease_rate.setter
    def quantum_decrease_rate(self, value):
        """Set quantum_decrease_rate"""
        if value is not None:
            try:
                self.__quantum_decrease_rate = float(value)
            except TypeError:
                raise ValueError("Invalid value type for quantum_decrease_rate, should be a float!")
        else:
            self.__quantum_decrease_rate = None

    @property
    def quantum_increase_rate(self):
        """Return quantum_increase_rate"""
        return self.__quantum_increase_rate

    @quantum_increase_rate.setter
    def quantum_increase_rate(self, value):
        """Set quantum_increase_rate"""
        if value is not None:
            try:
                self.__quantum_increase_rate = float(value)
            except TypeError:
                raise ValueError("Invalid value type for quantum_increase_rate, should be a float!")
        else:
            self.__quantum_increase_rate = None

    @property
    def uplink_bw_threshold(self):
        """Return uplink_bw_threshold"""
        return self.__uplink_bw_threshold

    @uplink_bw_threshold.setter
    def uplink_bw_threshold(self, value):
        """Set uplink_bw_threshold"""
        if value is not None:
            try:
                self.__uplink_bw_threshold = float(value)
            except TypeError:
                raise ValueError("Invalid value type for uplink_bw_threshold, should be a float!")
        else:
            self.__uplink_bw_threshold = None

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
    def active(self):
        """Return active."""
        return self.__active

    @active.setter
    def active(self, value):
        """Set active."""
        self.__active = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        self.__adaptive_slice_manager['active'] = self.__active
        self.__adaptive_slice_manager['min_quantum'] = self.__minimum_quantum
        self.__adaptive_slice_manager['max_quantum'] = self.__maximum_quantum
        self.__adaptive_slice_manager['inc_rate'] = self.__quantum_increase_rate
        self.__adaptive_slice_manager['dec_rate'] = self.__quantum_decrease_rate
        self.__adaptive_slice_manager['uplink_bw_threshold'] = self.__uplink_bw_threshold
        return self.__adaptive_slice_manager


def launch(tenant_id, minimum_quantum, maximum_quantum, quantum_decrease_rate, quantum_increase_rate, uplink_bw_threshold, db_monitor, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return AdaptiveSliceManager(tenant_id=tenant_id,
                                minimum_quantum=minimum_quantum,
                                maximum_quantum=maximum_quantum,
                                quantum_decrease_rate=quantum_decrease_rate,
                                quantum_increase_rate=quantum_increase_rate,
                                uplink_bw_threshold=uplink_bw_threshold,
                                db_monitor=db_monitor,
                                every=every)
