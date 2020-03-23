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
import json
import subprocess


class FlowManager(EmpowerApp):
    """Flow Manager App

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.sandbox.managers.flowmanager.flowmanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__flow_manager = {'message': 'Flow Manager is online!',
                               'flows': None,
                               'active_list': [],
                               'lvap_flow_map': {},
                               'lvap_load_expected_map': {}}
        self.__process_handler = {'flows': {}}
        self.__descriptor_filename = 'empower/apps/sandbox/managers/flowmanager/descriptors/' + str(
            self.descriptor)

        try:
            with open(self.__descriptor_filename) as f:
                self.__flow_manager['flows'] = json.load(f)['flows']
                self.create_lvap_flow_and_load_expected_map()
                self.create_mgen_scripts()

                # Run flows with mgen
                self.start_flows()
        except TypeError:
            raise ValueError("Invalid value for input file or file does not exist!")

    def loop(self):
        """Periodic job."""
        self.log.debug("Flow Manager APP loop...")
        if self.__flow_manager['active_list']:
            self.check_flows_status()

    def create_lvap_flow_and_load_expected_map(self):
        for flow_id in self.__flow_manager['flows']:
            crr_lvap_addr = self.__flow_manager['flows'][flow_id]['lvap_addr']
            if crr_lvap_addr not in self.__flow_manager['lvap_flow_map']:
                self.__flow_manager['lvap_flow_map'][crr_lvap_addr] = []
                self.__flow_manager['lvap_load_expected_map'][crr_lvap_addr] = 0
            self.__flow_manager['lvap_flow_map'][crr_lvap_addr].append(flow_id)
            self.__flow_manager['lvap_load_expected_map'][crr_lvap_addr] += self.__flow_manager['flows'][flow_id][
                'req_throughput_mbps']

    def check_flows_status(self):
        for flow_id in self.__flow_manager['active_list']:
            if self.__process_handler['flows'][flow_id].poll() is not None:
                self.__flow_manager['flows'][flow_id]['active'] = False
                self.__flow_manager['active_list'].remove(flow_id)

    def start_flows(self):
        for flow_id in self.__flow_manager['flows']:
            flow = self.__flow_manager['flows'][flow_id]
            if not flow['active']:
                mgen_command = ['mgen', 'input',
                                'empower/apps/sandbox/managers/flowmanager/scripts/mgen/flow' + str(flow_id) + '.mgn']
                self.__process_handler['flows'][flow_id] = subprocess.Popen(mgen_command)
                flow['active'] = True
                self.__flow_manager['active_list'].append(flow_id)

    def create_mgen_scripts(self):
        # Creating mgen script and execute it
        for flow_id in self.__flow_manager['flows']:
            multiplier = 1
            flow = self.__flow_manager['flows'][flow_id]
            # For the POISSON and PERIODIC distributions, 120 pps = 1Mbps
            multiplier = 120
            try:
                with open('empower/apps/sandbox/managers/flowmanager/scripts/mgen/flow' + str(flow_id) + '.mgn',
                          'w+') as mgen_file:
                    mgen_file.write(
                        str(flow['from']) + ' ' + 'ON ' + str(flow_id) + ' ' + str(
                            flow['protocol']) + ' ' + 'DST ' + str(
                            flow['dst_ip_addr']) + '/' + str(flow['port']) + ' ' + str(
                            flow['distribution']) + ' [' + str(
                            int(flow['req_throughput_mbps'] * multiplier)) + ' ' + str(flow['pkt_size']) + ']\n' + str(
                            flow['until']) + ' OFF ' + str(flow_id) + '\n')
                mgen_file.close()

            except TypeError:
                raise ValueError("Invalid path for mgen script files!")

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


def launch(tenant_id, descriptor, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return FlowManager(tenant_id=tenant_id,
                       descriptor=descriptor,
                       every=every)
