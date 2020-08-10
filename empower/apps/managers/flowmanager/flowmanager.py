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

"""Flow Manager App."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD

import subprocess


class FlowManager(EmpowerApp):
    """Flow Manager App

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.managers.flowmanager.flowmanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__flow_manager = {'message': 'Flow Manager is online!',
                               'flows': {},
                               'be_flows': [],
                               'be_slices': [],
                               'qos_flows': [],
                               'qos_slices': [],
                               'lvap_flow_map': {},                 # downlink flow map
                               'lvap_load_expected_map': {},        # downlink expected load
                               'network_flow_map': {},              # TODO: uplink flow map
                               'network_load_expected_map': {}}     # TODO: uplink expected load
        self.__process_handler = {'flows': {}}

        # Flow params
        self.__flow_id = None
        self.__flow_type = None
        self.__flow_dscp = None
        self.__flow_protocol = None
        self.__flow_distribution = None
        self.__flow_frame_size = None
        self.__flow_bw_req_mbps = None
        self.__flow_delay_req_ms = None
        self.__flow_dst_ip_addr = None
        self.__flow_dst_port = None
        self.__flow_dst_mac_addr = None
        self.__flow_duration = None

    def reset_flow_parameters(self):
        self.__flow_id = None
        self.__flow_type = None
        self.__flow_dscp = None
        self.__flow_protocol = None
        self.__flow_distribution = None
        self.__flow_frame_size = None
        self.__flow_bw_req_mbps = None
        self.__flow_delay_req_ms = None
        self.__flow_dst_ip_addr = None
        self.__flow_dst_port = None
        self.__flow_dst_mac_addr = None
        self.__flow_duration = None

    def loop(self):
        """Periodic job."""
        self.check_flow_status()

    def check_flow_status(self):
        flow_processes_to_expire = []
        for flow_id in self.__process_handler['flows']:
            if self.__process_handler['flows'][flow_id].poll() is not None:
                # expire flow
                self.remove_flow(flow_id)
                flow_processes_to_expire.append(flow_id)

        for flow_proc in flow_processes_to_expire:
            del self.__process_handler['flows'][flow_proc]

    def create_and_run_mgen_script(self):
        # For the POISSON and PERIODIC distributions, 120 pps = 1Mbps
        multiplier = 120
        try:
            with open('empower/apps/managers/flowmanager/scripts/mgen/flow' + str(self.__flow_id) + '.mgn',
                      'w+') as mgen_file:
                mgen_file.write(
                    str('0.0 ' + 'ON ' + str(self.__flow_id) + ' ' + str(self.__flow_protocol) + ' ' + 'DST ' + str(
                        self.__flow_dst_ip_addr) + '/' + str(self.__flow_dst_port) + ' ' + str(
                        self.__flow_distribution) + ' [' + str(int(self.__flow_bw_req_mbps * multiplier)) + ' ' + str(
                        self.__flow_frame_size) + ']\n' + str(self.__flow_duration) + ' OFF ' + str(
                        self.__flow_id) + '\n'))
                mgen_file.close()

                # mgen command
                mgen_command = ['mgen', 'input',
                                'empower/apps/managers/flowmanager/scripts/mgen/flow' + str(self.__flow_id) + '.mgn']

                self.__process_handler['flows'][self.__flow_id] = subprocess.Popen(mgen_command)
                return True
        except TypeError:
            raise ValueError("Invalid path for mgen script files!")
        return False

    def create_sleep_process(self):
        # For the uplink flow tracking
        try:
            sleep_command = ['sleep', str(self.__flow_duration)]
            self.__process_handler['flows'][self.__flow_id] = subprocess.Popen(sleep_command)
            return True
        except TypeError:
            raise ValueError("Error creating sleep process!")
        return False

    def add_flow(self):
        flow = {
            'flow_type': self.__flow_type,
            'flow_dscp': self.__flow_dscp,
            'flow_protocol': self.__flow_protocol,
            'flow_distribution': self.__flow_distribution,
            'flow_frame_size': self.__flow_frame_size,
            'flow_bw_req_mbps': self.__flow_bw_req_mbps,
            'flow_delay_req_ms': self.__flow_delay_req_ms,
            'flow_dst_ip_addr': self.__flow_dst_ip_addr,
            'flow_dst_mac_addr': self.__flow_dst_mac_addr,
            'flow_dst_port': self.__flow_dst_port,
            'flow_duration': self.__flow_duration
        }

        # If modifying a flow
        if self.__flow_id in self.__flow_manager['flows']:
            self.remove_flow(self.__flow_id)

        # fill in QoS and BE flow list
        if self.__flow_type == 'QoS':
            self.__flow_manager['qos_flows'].append(self.__flow_id)
            if self.__flow_dscp is not None:
                self.__flow_manager['qos_slices'].append(self.__flow_dscp)
        else:
            self.__flow_manager['be_flows'].append(self.__flow_id)
            if self.__flow_dscp is not None:
                self.__flow_manager['be_slices'].append(self.__flow_dscp)

        current_lvaps = []
        for lvap in self.lvaps():
            current_lvaps.append(str(lvap.addr))

        # if DST is a LVAP (downlink)
        if self.__flow_dst_mac_addr in current_lvaps:
            # fill in LVAP's flow list
            if self.__flow_dst_mac_addr not in self.__flow_manager['lvap_flow_map']:
                self.__flow_manager['lvap_flow_map'][self.__flow_dst_mac_addr] = []
            self.__flow_manager['lvap_flow_map'][self.__flow_dst_mac_addr].append(self.__flow_id)

            # fill in LVAP's flow load list
            if self.__flow_dst_mac_addr not in self.__flow_manager['lvap_load_expected_map']:
                self.__flow_manager['lvap_load_expected_map'][self.__flow_dst_mac_addr] = []
            self.__flow_manager['lvap_load_expected_map'][self.__flow_dst_mac_addr].append(self.__flow_bw_req_mbps)
        else:
            # it is an uplink flow
            if self.__flow_dst_mac_addr not in self.__flow_manager['network_flow_map']:
                self.__flow_manager['network_flow_map'][self.__flow_dst_mac_addr] = []
            self.__flow_manager['network_flow_map'][self.__flow_dst_mac_addr].append(self.__flow_id)

            # fill in network flow load into list
            if self.__flow_dst_mac_addr not in self.__flow_manager['network_load_expected_map']:
                self.__flow_manager['network_load_expected_map'][self.__flow_dst_mac_addr] = []
            self.__flow_manager['network_load_expected_map'][self.__flow_dst_mac_addr].append(self.__flow_bw_req_mbps)

            # creating sleep process to track uplink flows
            self.create_sleep_process()

        # add flow structure
        self.__flow_manager['flows'][self.__flow_id] = flow

    def remove_flow(self, flow_id):
        flow = self.__flow_manager['flows'][flow_id]

        del self.__flow_manager['flows'][flow_id]
        if flow['flow_type'] == 'QoS':
            self.__flow_manager['qos_flows'].remove(flow_id)
            if self.__flow_dscp is not None:
                self.__flow_manager['qos_slices'].remove(flow['flow_dscp'])
        else:
            self.__flow_manager['be_flows'].remove(flow_id)
            if self.__flow_dscp is not None:
                self.__flow_manager['be_slices'].remove(flow['flow_dscp'])

        # remove from lvap flow map
        if flow['flow_dst_mac_addr'] in self.__flow_manager['lvap_flow_map']:
            if flow_id in self.__flow_manager['lvap_flow_map'][flow['flow_dst_mac_addr']]:
                self.__flow_manager['lvap_flow_map'][flow['flow_dst_mac_addr']].remove(flow_id)

        if flow['flow_dst_mac_addr'] in self.__flow_manager['lvap_load_expected_map']:
            if flow_id in self.__flow_manager['lvap_load_expected_map'][flow['flow_dst_mac_addr']]:
                self.__flow_manager['lvap_load_expected_map'][flow['flow_dst_mac_addr']].remove(flow['flow_bw_req_mbps'])

        # remove from network flow map
        if flow['flow_dst_mac_addr'] in self.__flow_manager['network_flow_map']:
            if flow_id in self.__flow_manager['network_flow_map'][flow['flow_dst_mac_addr']]:
                self.__flow_manager['network_flow_map'][flow['flow_dst_mac_addr']].remove(flow_id)

        if flow['flow_dst_mac_addr'] in self.__flow_manager['network_load_expected_map']:
            if flow_id in self.__flow_manager['network_load_expected_map'][flow['flow_dst_mac_addr']]:
                self.__flow_manager['network_load_expected_map'][flow['flow_dst_mac_addr']].remove(flow['flow_bw_req_mbps'])

        if flow_id in self.__process_handler['flows']:
            if self.__process_handler['flows'][flow_id].poll() is None:
                self.__process_handler['flows'][flow_id].kill()

    @property
    def start_flow(self):
        """Return start_flow."""

        return self.__start_flow

    @start_flow.setter
    def start_flow(self, value):
        """Set start_flow."""

        if value is not None:
            if self.create_and_run_mgen_script():
                self.log.debug("Starting flow using MGEN!")
            else:
                raise ValueError("Could not start flow with MGEN!")
            self.reset_flow_parameters()

    @property
    def flow_id(self):
        """Return flow_id."""

        return self.__flow_id

    @flow_id.setter
    def flow_id(self, value):
        """Set flow_id."""

        self.__flow_id = value

    @property
    def flow_type(self):
        """Return flow_type."""

        return self.__flow_type

    @flow_type.setter
    def flow_type(self, value):
        """Set flow_type."""

        self.__flow_type = value

    @property
    def flow_dscp(self):
        """Return flow_dscp."""

        return self.__flow_dscp

    @flow_dscp.setter
    def flow_dscp(self, value):
        """Set flow_dscp."""

        self.__flow_dscp = value

    @property
    def flow_protocol(self):
        """Return flow_protocol."""

        return self.__flow_protocol

    @flow_protocol.setter
    def flow_protocol(self, value):
        """Set flow_protocol."""

        self.__flow_protocol = value

    @property
    def flow_distribution(self):
        """Return flow_distribution."""

        return self.__flow_distribution

    @flow_distribution.setter
    def flow_distribution(self, value):
        """Set flow_distribution."""

        self.__flow_distribution = value

    @property
    def flow_frame_size(self):
        """Return flow_frame_size."""

        return self.__flow_frame_size

    @flow_frame_size.setter
    def flow_frame_size(self, value):
        """Set flow_frame_size."""

        self.__flow_frame_size = value

    @property
    def flow_bw_req_mbps(self):
        """Return flow_bw_req_mbps."""

        return self.__flow_bw_req_mbps

    @flow_bw_req_mbps.setter
    def flow_bw_req_mbps(self, value):
        """Set flow_bw_req_mbps."""

        self.__flow_bw_req_mbps = value

    @property
    def flow_delay_req_ms(self):
        """Return flow_delay_req_ms."""

        return self.__flow_delay_req_ms

    @flow_delay_req_ms.setter
    def flow_delay_req_ms(self, value):
        """Set flow_delay_req_ms."""

        self.__flow_delay_req_ms = value

    @property
    def flow_dst_ip_addr(self):
        """Return flow_dst_ip_addr."""

        return self.__flow_dst_ip_addr

    @flow_dst_ip_addr.setter
    def flow_dst_ip_addr(self, value):
        """Set flow_dst_ip_addr."""

        self.__flow_dst_ip_addr = value

    @property
    def flow_dst_port(self):
        """Return flow_dst_port."""

        return self.__flow_dst_port

    @flow_dst_port.setter
    def flow_dst_port(self, value):
        """Set flow_dst_port."""

        self.__flow_dst_port = value

    @property
    def flow_dst_mac_addr(self):
        """Return flow_dst_mac_addr."""

        return self.__flow_dst_mac_addr

    @flow_dst_mac_addr.setter
    def flow_dst_mac_addr(self, value):
        """Set flow_dst_mac_addr."""

        self.__flow_dst_mac_addr = value

    @property
    def flow_duration(self):
        """Return flow_duration."""

        return self.__flow_duration

    @flow_duration.setter
    def flow_duration(self, value):
        """Set flow_duration."""
        if isinstance(value, int):
            if value >= 0:
                self.__flow_duration = value
                self.add_flow()
            else:
                self.reset_flow_parameters()
                raise ValueError(
                    "Invalid value for flow duration, flow duration needs to be greater than or equal to 0!")
        else:
            self.reset_flow_parameters()
            raise ValueError("Invalid value type for flow duration, integer required!")
    
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
    def flow_manager(self):
        """Return default Flow Manager"""
        return self.__flow_manager

    @flow_manager.setter
    def flow_manager(self, value):
        """Set Flow Manager"""
        self.__flow_manager = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__flow_manager


def launch(tenant_id, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return FlowManager(tenant_id=tenant_id,
                       every=every)
