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

"""Adaptive LVAP Manager App."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_CONTROL_PERIOD
from empower.main import RUNTIME

import socket
import threading

DEFAULT_PORT = 7777
DEFAULT_TIMEOUT = 10


class AdaptiveLVAPManager(EmpowerApp):
    """Adaptive LVAP Manager App

    Command Line Parameters:
        tenant_id: tenant id
        minimum_bw: minimum_bw,
        maximum_bw: maximum_bw,
        bw_decrease_rate: bw_decrease_rate,
        bw_increase_rate: bw_increase_rate,
        db_monitor: db_monitor,
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.managers.adaptivelvapmanager.adaptivelvapmanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            --minimum_bw=0
            --minimum_bw=100
            --bw_increase_rate=0.1
            --bw_decrease_rate=0.1
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__adaptive_lvap_manager = {
            "message": "Adaptive LVAP Manager is online!",
            "configs": {}
        }
        self.__lvap_stats_handler = None
        self.__active_flows_handler = None
        self.__active = True
        self.__adaptive_lvap_manager['active'] = self.__active
        self.__minimum_bw = self.minimum_bw
        self.__maximum_bw = self.maximum_bw
        self.__bw_decrease_rate = self.bw_decrease_rate
        self.__bw_increase_rate = self.bw_increase_rate

    def loop(self):
        """Periodic job."""
        if self.__active:
            if self.get_slice_stats() and self.get_active_flows() and self.get_lvap_stats():

                # Get LVAP current configs
                self.get_lvap_configs()

                # Run only when there are QoS flows
                if self.__active_flows_handler['qos_flows']:
                    for crr_wtp_addr in self.__slice_stats_handler['wtps']:
                        if self.requirements_met(wtp=crr_wtp_addr):
                            factor = self.__bw_increase_rate
                        else:
                            factor = self.__bw_decrease_rate

                        # Reconfigure all LVAP in the WTP
                        self.reconfigure(factor, crr_wtp_addr)
                else:
                    for crr_wtp_addr in self.__slice_stats_handler['wtps']:
                        # Reconfigure all slices in the WTP
                        self.reset_all_lvap_configs()

            if self.__db_monitor is not None:
                for lvap_addr in self.__adaptive_lvap_manager['configs']:
                    fields = ['LVAP_ADDR', 'BW_SHAPER_MBPS']
                    crr_bw_shaper = self.__adaptive_lvap_manager['configs'][lvap_addr]['crr_bw_shaper_mbps']
                    values = [lvap_addr, crr_bw_shaper]

                    # Saving into db
                    self.monitor.insert_into_db(table='lvap_shaping', fields=fields, values=values)

                fields = ['MIN_BW_MBPS', 'MAX_BW_MBPS', 'INC_RATE', 'DEC_RATE']
                values = [self.__minimum_bw, self.__maximum_bw,
                          self.__bw_increase_rate, self.__bw_decrease_rate]

                # Saving into db
                self.monitor.insert_into_db(table='adaptive_shaping', fields=fields, values=values)

                # Keeping only the last measurements in db
                self.monitor.keep_last_measurements_only('adaptive_shaping')
                self.monitor.keep_last_measurements_only('lvap_shaping')

    def reset_all_lvap_configs(self):
        for lvap_addr in self.__adaptive_lvap_manager['configs']:
            crr_bw_shaper = self.__adaptive_lvap_manager['configs'][lvap_addr]['crr_bw_shaper_mbps']
            if self.__maximum_bw != crr_bw_shaper:
                self.send_config_to_lvap(lvap_addr=lvap_addr,
                                         ip_addr=self.__adaptive_lvap_manager['configs'][lvap_addr]['ip_addr'],
                                         new_bw_shaper=self.__maximum_bw)

    def reconfigure(self, factor, crr_wtp_addr):
        for lvap in self.lvaps():
            wtp = str(lvap.blocks[0].addr)
            lvap_addr = str(lvap.addr)
            # If LVAP is connected to the WTP
            if crr_wtp_addr == wtp:
                if lvap_addr in self.__adaptive_lvap_manager['configs']:
                    if self.__adaptive_lvap_manager['configs'][lvap_addr]['flow_type'] == 'BE':
                        sta_rx_bw_mean = self.__lvap_stats_handler['lvaps'][lvap_addr]['rx_throughput_mbps']['mean']
                        # only if the slice active...
                        if sta_rx_bw_mean > 0:
                            crr_bw_shaper = self.__adaptive_lvap_manager['configs'][lvap_addr]['crr_bw_shaper_mbps']
                            ip_addr = self.__adaptive_lvap_manager['configs'][lvap_addr]['ip_addr']
                            adapted_bw_shaper = float(crr_bw_shaper * factor)
                            if adapted_bw_shaper > self.__maximum_bw:
                                adapted_bw_shaper = self.__maximum_bw
                            if adapted_bw_shaper < self.__minimum_bw:
                                adapted_bw_shaper = self.__minimum_bw
                            if adapted_bw_shaper != crr_bw_shaper:
                                self.send_config_to_lvap(lvap_addr=lvap_addr,
                                                         ip_addr=ip_addr,
                                                         new_bw_shaper=adapted_bw_shaper)

    def requirements_met(self, wtp):
        for qos_flow_id in self.__active_flows_handler['qos_flows']:
            qos_flow = self.__active_flows_handler['flows'][qos_flow_id]
            # If downlink QoS flow
            if qos_flow['flow_dscp'] in self.__slice_stats_handler['wtps'][wtp]['slices']:
                # Checking queueing delay
                queue_delay_median = \
                    self.__slice_stats_handler['wtps'][wtp]['slices'][qos_flow['flow_dscp']]['queue_delay_ms']['median']
                if queue_delay_median is not None and qos_flow['flow_delay_req_ms'] is not None:
                    if qos_flow['flow_delay_req_ms'] < queue_delay_median:
                        return False
                # Checking throughput
                slc_throughput_mbps_mean = \
                    self.__slice_stats_handler['wtps'][wtp]['slices'][qos_flow['flow_dscp']]['throughput_mbps']['median']
                if slc_throughput_mbps_mean is not None and qos_flow['flow_bw_req_mbps'] is not None:
                    if qos_flow['flow_bw_req_mbps'] < slc_throughput_mbps_mean:
                        return False

            # If uplink QoS flow
            elif qos_flow['flow_dscp'] is None:
                if 'flow_src_mac_addr' in qos_flow:
                    if qos_flow['flow_src_mac_addr'] in self.__lvap_stats_handler['lvaps']:
                        # Checking throughput
                        sta_rx_bw_mean = \
                            self.__lvap_stats_handler['lvaps'][qos_flow['flow_src_mac_addr']]['rx_throughput_mbps']['mean']
                        if sta_rx_bw_mean is not None:
                            # less bw that required...
                            if sta_rx_bw_mean < qos_flow['flow_bw_req_mbps']:
                                # Search if the LVAP is connected to the WTP being analyzed
                                for lvap in self.lvaps():
                                    if str(lvap.addr) == qos_flow['flow_src_mac_addr']:
                                        if str(lvap.blocks[0].addr) == wtp:
                                            return False
        return True

    def get_lvap_configs(self):
        for flow_id in self.__active_flows_handler['flows']:
            flow = self.__active_flows_handler['flows'][flow_id]
            # If it is an uplink QoS flow
            if flow['flow_dscp'] is None:
                if 'flow_src_mac_addr' in flow:
                    if flow['flow_src_mac_addr'] not in self.__adaptive_lvap_manager['configs']:
                        self.__adaptive_lvap_manager['configs'][flow['flow_src_mac_addr']] = {
                            'ip_addr': flow['flow_src_ip_addr'],
                            'crr_bw_shaper_mbps': self.__maximum_bw,
                            'flow_type': flow['flow_type']
                        }
                        # Instead of getting the values, we set the max bw shaper as an initial value
                        self.send_config_to_lvap(lvap_addr=flow['flow_src_mac_addr'],
                                                 ip_addr=flow['flow_src_ip_addr'],
                                                 new_bw_shaper=self.__maximum_bw)
                    # else:
                    #     self.__adaptive_lvap_manager['configs'][flow['flow_src_mac_addr']]['ip_addr'] = flow[
                    #         'flow_src_ip_addr']
                    #     self.__adaptive_lvap_manager['configs'][flow['flow_src_mac_addr']]['flow_type'] = flow[
                    #         'flow_type']
                    #     # Try getting config from LVAP (parsing needed)
                    #     # This might be too slow so there is a timeout for the socket connection
                    #     self.get_config_from_lvap(lvap_addr=flow['flow_src_mac_addr'])

    # def get_config_from_lvap(self, lvap_addr):
    #     if lvap_addr is not None:
    #         thread = threading.Thread(target=self.get_config, kwargs=dict(lvap_addr=lvap_addr))
    #         thread.daemon = True
    #         thread.start()
    #     else:
    #         self.log.debug("IP address is not set, aborting!")
    #
    # def get_config(self, lvap_addr):
    #     try:
    #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #             s.settimeout(DEFAULT_TIMEOUT)  # timeout
    #             ip_addr = self.__adaptive_lvap_manager['configs'][lvap_addr]['ip_addr']
    #             s.connect((str(ip_addr), DEFAULT_PORT))
    #             cmd = "READ bw_shaper.rate\n"
    #             s.sendall(cmd.encode())
    #             data = s.recv(1024)
    #             self.log.debug(
    #                 "Getting new configurations from LVAP IP " + str(ip_addr) + ":" + str(DEFAULT_PORT) + " - " + str(
    #                     repr(data)))
    #             crr_bw_shaper = data.decode("utf-8").splitlines()[-1]
    #             if 'Mbps' in crr_bw_shaper:
    #                 crr_bw_shaper = crr_bw_shaper.replace('Mbps', '')
    #                 crr_bw_shaper = float(crr_bw_shaper) if '.' in crr_bw_shaper else int(crr_bw_shaper)
    #                 self.__adaptive_lvap_manager['configs'][lvap_addr]['crr_bw_shaper_mbps'] = crr_bw_shaper
    #
    #                 if self.__db_monitor is not None:
    #                     fields = ['LVAP_ADDR', 'BW_SHAPER_MBPS']
    #                     values = [lvap_addr, crr_bw_shaper]
    #
    #                     # Saving into db
    #                     self.monitor.insert_into_db(table='lvap_shaping', fields=fields, values=values)
    #     except:
    #         raise ValueError("Timeout getting configuration from LVAP", ip_addr, DEFAULT_PORT)

    def send_config_to_lvap(self, lvap_addr, ip_addr, new_bw_shaper):
        if ip_addr is not None:
            thread = threading.Thread(target=self.send_config,
                                      kwargs=dict(lvap_addr=lvap_addr,
                                                  ip_addr=ip_addr,
                                                  new_bw_shaper=(new_bw_shaper)))
            thread.daemon = True
            thread.start()
        else:
            self.log.debug("IP address is not set, aborting configuration!")

    def send_config(self, lvap_addr, ip_addr, new_bw_shaper):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(DEFAULT_TIMEOUT)  # timeout
            s.connect((str(ip_addr), DEFAULT_PORT))
            cmd = "WRITE "
            if new_bw_shaper is not None:
                cmd_bw_shaper = cmd + "bw_shaper.rate " + str(new_bw_shaper * 125000) + "\n"
                s.sendall(cmd_bw_shaper.encode())
                data = s.recv(1024)
                self.log.debug(
                    "Sending new configurations to LVAP: IP " + str(ip_addr) + ":" + str(DEFAULT_PORT) + " - " + str(
                        new_bw_shaper) + " - " + str(repr(data)))

                # Update JSON to track traffic shapers
                self.__adaptive_lvap_manager['configs'][lvap_addr]['crr_bw_shaper_mbps'] = new_bw_shaper

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

    def get_lvap_stats(self):
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
    def adaptive_lvap_manager(self):
        """Return default Adaptive LVAP Manager"""
        return self.__adaptive_lvap_manager

    @adaptive_lvap_manager.setter
    def adaptive_lvap_manager(self, value):
        """Set Adaptive LVAP Manager"""
        self.__adaptive_lvap_manager = value

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
        self.__adaptive_lvap_manager['active'] = self.__active
        self.__adaptive_lvap_manager['min_bw'] = self.__minimum_bw
        self.__adaptive_lvap_manager['max_bw'] = self.__maximum_bw
        self.__adaptive_lvap_manager['inc_rate'] = self.__bw_increase_rate
        self.__adaptive_lvap_manager['dec_rate'] = self.__bw_decrease_rate
        self.__adaptive_lvap_manager['default_port'] = DEFAULT_PORT
        return self.__adaptive_lvap_manager


def launch(tenant_id, minimum_bw, maximum_bw, bw_decrease_rate, bw_increase_rate, db_monitor, every=DEFAULT_CONTROL_PERIOD):
    """ Initialize the module. """

    return AdaptiveLVAPManager(tenant_id=tenant_id,
                               minimum_bw=minimum_bw,
                               maximum_bw=maximum_bw,
                               bw_decrease_rate=bw_decrease_rate,
                               bw_increase_rate=bw_increase_rate,
                               db_monitor=db_monitor,
                               every=every)
