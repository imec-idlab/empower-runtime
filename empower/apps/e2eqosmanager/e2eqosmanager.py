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

"""End-to-end QoS Manager App"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.datatypes.dscp import DSCP
from empower.main import RUNTIME

from empower.apps.e2eqosmanager.parsers.slice_request import format_slice_add_request

# Heuristic
from empower.apps.e2eqosmanager.algorithms.exponentialquantumadaptation import ExponentialQuantumAdaptation

import json
import time


class E2EQoSManager(EmpowerApp):
    """End-to-End QoS Manager App

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Slice Configuration:
    Add:
    {
        "version": 1.0,
        "dscp": "0x42",
        "wifi": {
            "static-properties": {
              "amsdu_aggregation": true,
              "quantum": 12000
            },
            "wtps": {
              "00:0D:B9:2F:56:64": {
                "static-properties": {
                  "quantum": 15000
                }
              }
            }
        },
        "lte": {
            "static-properties": {
              "rbgs": 5,
              "sched_id": 1
            },
            "vbses": {
                "aa:bb:cc:dd:ee:ff": {
                    "static-properties": {
                      "rbgs": 2
                    },
                }
            }
        }
    }

    Delete:
    DSCP value


    Example:
        ./empower-runtime.py apps.e2eqosmanager.e2eqosmanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lvap_stats_descriptor = None
        self.__linear_quantum_adaptation = ExponentialQuantumAdaptation()
        self.__experiment_file = open("experiment_quantum_adaptive.txt", "w")
        self.__experiment_file.write("Timestamp,Slice 1 DSCP,Quantum,Slice 2 DSCP,Quantum\n")

        # Config Files
        self.__e2e_qos_file_path = self.e2e_qos_file_path
        self.__slices_file_path = self.slices_file_path

        # Load traffic descriptor from JSON
        try:
            self.__e2e_qos_descriptor = json.loads(open(self.__e2e_qos_file_path).read())
            self.__slices_descriptor = json.loads(open(self.__slices_file_path).read())  # Load initial slices
        except TypeError:
            raise ValueError("Invalid value for config files or files do not exist!")

        self.__init_slices_flag = True

    def loop(self):
        """Periodic job."""
        self.log.debug('E2E QoS Manager Loop...')
        if self.__init_slices_flag:
            # Initialize slices
            self.change_slices_configuration()  # Create initial slices (should be one per service)
            self.__init_slices_flag = False

        # If stats are being collected
        if 'empower.apps.handlers.lvapstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__lvap_stats_descriptor = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.lvapstatshandler'].to_dict()
            print(self.__lvap_stats_descriptor)

            # For each lvap with QoS requirements
            for lvap_addr in self.__e2e_qos_descriptor:
                if lvap_addr in self.__lvap_stats_descriptor:
                    # If there is data
                    if self.__lvap_stats_descriptor[lvap_addr]['metrics']['latency']['median'] is not None and \
                            self.__lvap_stats_descriptor[lvap_addr]['metrics']['throughput']['tx_mbits_per_second']['median'] is not None:
                        # 1 - Check if Latency QoS requirements are met!
                        if self.__e2e_qos_descriptor[lvap_addr]['metrics']['latency'] <= \
                                self.__lvap_stats_descriptor[lvap_addr]['metrics']['latency']['median']:
                            self.__linear_quantum_adaptation.exploit()
                        else:
                            self.__linear_quantum_adaptation.explore()

                        # 2 - Change quantum in runtime
                        # Algorithm: Exponential Quantum Adaptation
                        slice_info = ""
                        for slice_dscp in self.__slices_descriptor:
                            if self.__slices_descriptor[slice_dscp]['type'] == 'best_effort':
                                # reduce 10% of quantum each round
                                new_quantum = self.__linear_quantum_adaptation.get_new_quantum(
                                    self.__slices_descriptor[slice_dscp]['quantum'])
                                if new_quantum != self.__slices_descriptor[slice_dscp]['quantum']:
                                    self.__slices_descriptor[slice_dscp]['quantum'] = new_quantum
                                    self.change_slices_configuration()
                            slice_info += "," + str(slice_dscp) + "," + str(self.__slices_descriptor[slice_dscp]['quantum'])
                        self.__experiment_file.write(str(time.time()) + slice_info + "\n")

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
    def lvap_stats_descriptor(self):
        """Return last LVAP stats."""
        return self.__lvap_stats_descriptor

    @lvap_stats_descriptor.setter
    def lvap_stats_descriptor(self, value):
        """Set last LVAP stats."""
        self.__lvap_stats_descriptor = value

    @property
    def e2e_qos_file_path(self):
        """Return e2e_qos_file_path"""
        return self.__e2e_qos_file_path

    @e2e_qos_file_path.setter
    def e2e_qos_file_path(self, value):
        """Set e2e_qos_file_path"""
        if isinstance(value, str):
            self.__e2e_qos_file_path = value
        else:
            raise ValueError("Invalid value type for e2e_qos_file_path, should be a string!")

    @property
    def e2e_qos_descriptor(self):
        """Return default e2e_qos_descriptor"""
        return self.__e2e_qos_descriptor

    @e2e_qos_descriptor.setter
    def e2e_qos_descriptor(self, value):
        """Set e2e_qos_descriptor"""
        self.__e2e_qos_descriptor = value

    @property
    def slices_file_path(self):
        """Return slices_file_path"""
        return self.__slices_file_path

    @slices_file_path.setter
    def slices_file_path(self, value):
        """Set slices_file_path"""
        if isinstance(value, str):
            self.__slices_file_path = value
        else:
            raise ValueError("Invalid value type for slices_file_path, should be a string!")

    @property
    def slices_descriptor(self):
        """Return default slices_descriptor"""
        return self.__slices_descriptor

    @slices_descriptor.setter
    def slices_descriptor(self, value):
        """Set slices_descriptor"""
        self.__slices_descriptor = value

    def to_dict(self):
        return 'E2E to_dict()... Expecting QoS Req vs Metrics!'

    def same_slice_values(self, crr_slice_descriptor, crr_tenant_slice):
        fields = ['quantum', 'amsdu_aggregation', 'scheduler']
        for field in fields:
            if crr_slice_descriptor[field] != crr_tenant_slice[field]:
                return False
        return True

    def change_slices_configuration(self):
        # For each slice configuration
        for slice_descriptor_dscp in self.slices_descriptor:
            crr_dscp = DSCP(slice_descriptor_dscp)
            if crr_dscp in self.tenant.slices:
                # Check if values are the same
                if not self.same_slice_values(self.slices_descriptor[slice_descriptor_dscp],
                                              self.tenant.slices[crr_dscp].wifi['static-properties']):
                    # Setting a new slice to replace the values from the existing one
                    new_slice = format_slice_add_request(slice_descriptor_dscp,
                                                         self.slices_descriptor[slice_descriptor_dscp]['quantum'],
                                                         self.slices_descriptor[slice_descriptor_dscp]['amsdu_aggregation'],
                                                         self.slices_descriptor[slice_descriptor_dscp]['scheduler'])
                    self.tenant.set_slice(DSCP(slice_descriptor_dscp), new_slice)
            else:
                # Add new ones
                new_slice = format_slice_add_request(slice_descriptor_dscp,
                                                     self.slices_descriptor[slice_descriptor_dscp]['quantum'],
                                                     self.slices_descriptor[slice_descriptor_dscp]['amsdu_aggregation'],
                                                     self.slices_descriptor[slice_descriptor_dscp]['scheduler'])
                self.tenant.add_slice(DSCP(slice_descriptor_dscp), new_slice)


def launch(tenant_id, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return E2EQoSManager(tenant_id=tenant_id,
                         e2e_qos_file_path="empower/apps/e2eqosmanager/configs/e2e_qos_descriptor_idlab.json",
                         slices_file_path="empower/apps/e2eqosmanager/configs/slices_descriptor.json",
                         every=every)