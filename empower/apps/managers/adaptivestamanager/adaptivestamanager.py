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

"""Adaptive STA Manager App."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.main import RUNTIME

DEFAULT_PORT = 7777


class WiFiSTAManager(EmpowerApp):
    """Adaptive STA Manager App

    Command Line Parameters:
        tenant_id: tenant id
        minimum_bw: minimum_bw,
        maximum_bw: maximum_bw,
        bw_decrease_rate: bw_decrease_rate,
        bw_increase_rate: bw_increase_rate,
        db_monitor: db_monitor,
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.managers.adaptivestamanager.adaptivestamanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            --minimum_bw=0
            --minimum_bw=100
            --bw_increase_rate=0.1
            --bw_decrease_rate=0.1
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__adaptive_sta_manager = {
            "message": "Adaptive STA Manager is online!",
            "configs": {}
        }
        self.__sta_stats_handler = None
        self.__active_flows_handler = None
        self.__active = True
        self.__adaptive_sta_manager['active'] = self.__active
        self.__minimum_bw = self.minimum_bw
        self.__maximum_bw = self.maximum_bw
        self.__bw_decrease_rate = self.bw_decrease_rate
        self.__bw_increase_rate = self.bw_increase_rate

    def loop(self):
        """Periodic job."""
        if self.__active:
            if self.get_sta_stats() and self.get_active_flows():
                # Run only when there are QoS flows
                if 'qos_flows' in self.__active_flows_handler:
                    # Check the uplink flows and get their configs (IP, bw_shaper)
                    self.get_sta_configs()
                    # TODO: check requirements

    # def reset_sta_config(self, lvap_addr):
        # TODO: Set the bw shaping to max value

    # def reconfigure(self, factor, lvap_addr):
        # TODO: Adapt the bw shaping applying the factor

    # def requirements_met(self, lvap_addr):
        # TODO: Check if both downlink and uplink QoS are met

    # def send_sta_config(self, new_bw, sta_ip_addr):
        # TODO: Open a socket and send the new bw shaping to the STA
    #     self.log.debug("Sending new configurations to STA")

    def get_sta_configs(self):
        for qos_flow_id in self.__active_flows_handler['qos_flows']:
            qos_flow = self.__active_flows_handler['flows'][qos_flow_id]
            # If it is an uplink QoS flow
            if qos_flow['flow_dscp'] is None:
                if 'flow_src_mac_addr' in qos_flow:
                    if qos_flow['flow_src_mac_addr'] not in self.__adaptive_sta_manager['configs']:
                        self.__adaptive_sta_manager['configs'][qos_flow['flow_src_mac_addr']] = {
                            'ip_addr': None,
                            'port': DEFAULT_PORT
                        }
                    if 'flow_src_ip_addr' in qos_flow:
                        self.__adaptive_sta_manager['configs'][qos_flow['flow_src_mac_addr']]['ip_addr'] = qos_flow[
                            'flow_src_ip_addr']

    def get_active_flows(self):
        if 'empower.apps.managers.flowmanager.flowmanager' in RUNTIME.tenants[self.tenant_id].components:
            self.__active_flows_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.managers.flowmanager.flowmanager'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.managers.flowmanager.flowmanager' is not online!")
            return False

    def get_sta_stats(self):
        if 'empower.apps.handlers.binstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__sta_stats_handler = RUNTIME.tenants[self.tenant_id].components[
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
    def sta_stats_handler(self):
        """Return default sta_stats_handler"""
        return self.__sta_stats_handler

    @sta_stats_handler.setter
    def sta_stats_handler(self, value):
        """Set sta_stats_handler"""
        self.__sta_stats_handler = value

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
    def adaptive_sta_manager(self):
        """Return default Adaptive STA Manager"""
        return self.__adaptive_sta_manager

    @adaptive_sta_manager.setter
    def adaptive_sta_manager(self, value):
        """Set Adaptive STA Manager"""
        self.__adaptive_sta_manager = value

    @property
    def minimum_bw(self):
        """Return minimum bw"""
        return self.__minimum_bw

    @minimum_bw.setter
    def minimum_bw(self, value):
        """Set minimum_bw"""
        if value is not None:
            try:
                self.__minimum_bw = int(value)
            except TypeError:
                raise ValueError("Invalid value type for minimum_bw, should be an integer!")
        else:
            self.__minimum_bw = None

    @property
    def maximum_bw(self):
        """Return maximum bw"""
        return self.__maximum_bw

    @maximum_bw.setter
    def maximum_bw(self, value):
        """Set maximum_bw"""
        if value is not None:
            try:
                self.__maximum_bw = int(value)
            except TypeError:
                raise ValueError("Invalid value type for maximum_bw, should be an integer!")
        else:
            self.__maximum_bw = 12000

    @property
    def bw_decrease_rate(self):
        """Return bw_decrease_rate"""
        return self.__bw_decrease_rate

    @bw_decrease_rate.setter
    def bw_decrease_rate(self, value):
        """Set bw_decrease_rate"""
        if value is not None:
            try:
                self.__bw_decrease_rate = float(value)
            except TypeError:
                raise ValueError("Invalid value type for bw_decrease_rate, should be a float!")
        else:
            self.__bw_decrease_rate = None

    @property
    def bw_increase_rate(self):
        """Return bw_increase_rate"""
        return self.__bw_increase_rate

    @bw_increase_rate.setter
    def bw_increase_rate(self, value):
        """Set bw_increase_rate"""
        if value is not None:
            try:
                self.__bw_increase_rate = float(value)
            except TypeError:
                raise ValueError("Invalid value type for bw_increase_rate, should be a float!")
        else:
            self.__bw_increase_rate = None

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
        self.__adaptive_sta_manager['active'] = self.__active
        self.__adaptive_sta_manager['min_bw'] = self.__minimum_bw
        self.__adaptive_sta_manager['max_bw'] = self.__maximum_bw
        self.__adaptive_sta_manager['inc_rate'] = self.__bw_increase_rate
        self.__adaptive_sta_manager['dec_rate'] = self.__bw_decrease_rate
        return self.__adaptive_sta_manager


def launch(tenant_id, minimum_bw, maximum_bw, bw_decrease_rate, bw_increase_rate, db_monitor, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return WiFiSTAManager(tenant_id=tenant_id,
                          minimum_bw=minimum_bw,
                          maximum_bw=maximum_bw,
                          bw_decrease_rate=bw_decrease_rate,
                          bw_increase_rate=bw_increase_rate,
                          db_monitor=db_monitor,
                          every=every)