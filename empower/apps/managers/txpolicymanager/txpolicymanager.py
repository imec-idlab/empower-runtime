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

"""TX Policy Manager APP."""

from empower.core.app import EmpowerApp
from empower.core.resourcepool import BT_HT20


class TxPolicyManager(EmpowerApp):
    """TX policy Manager APP.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__ht_mcs = self.ht_mcs
        self.__tx_policy_manager = {"message": "TX policy Manager is online!", 'ht_mcs': self.__ht_mcs}

    def config_tx_policy(self, lvap, blocks):
        for block in blocks:
            # Check block band to apply the MCS
            if block.band == BT_HT20:
                # Creating transmission policy
                tx_policy = block.tx_policies[lvap.addr]
                tx_policy.ht_mcs = self.__ht_mcs
                self.log.debug("Block %s setting mac_address %s, ht_mcs %s",
                               block,
                               str(lvap.addr),
                               str(tx_policy.ht_mcs))
            else:
                self.log.debug("WTP Block does not support ht_mcs, applying default configuration!")

    def lvap_join(self, lvap):
        """Called when an LVAP joins a tenant."""
        if self.ht_mcs is not None:
            self.config_tx_policy(lvap, self.blocks())

    def lvap_handover(self, lvap, source_blocks):
        """Called when an LVAP completes a handover."""
        if self.ht_mcs is not None:
            self.config_tx_policy(lvap, source_blocks)

    @property
    def ht_mcs(self):
        """Return default ht_mcs"""
        return self.__ht_mcs

    @ht_mcs.setter
    def ht_mcs(self, value):
        """Set ht_mcs"""

        self.__ht_mcs = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        self.__tx_policy_manager['ht_mcs'] = self.__ht_mcs
        return self.__tx_policy_manager


def launch(tenant_id, ht_mcs=[0, 1, 2, 3, 4, 5, 6, 7]):  # Raspberry pis have only 1 spatial stream
    """ Initialize the module. """

    return TxPolicyManager(tenant_id=tenant_id, ht_mcs=ht_mcs)
