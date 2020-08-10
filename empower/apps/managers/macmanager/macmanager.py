#!/usr/bin/env python3
#
# Copyright (c) 2018 Pedro Heleno Isolani
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

"""MAC Manager App."""

from empower.core.app import EmpowerApp

from empower.datatypes.etheraddress import EtherAddress

from empower.core.app import DEFAULT_PERIOD
from empower.core.resourcepool import BT_HT20


class MACManager(EmpowerApp):
    """MAC Manager App.

    Command Line Parameters:

        tenant_id: tenant id
        mac_address: destination mac address where the mcs is going to be changed
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.managers.macmanager.macmanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            --mac_address="98:01:A7:BE:D0:5D"
            --mcs=[6.0,
                   9.0,
                   12.0,
                   18.0,
                   24.0,
                   36.0,
                   48.0,
                   54.0]
            --ht_mcs=[0,
                      1,
                      2,
                      3,
                      4,
                      5,
                      6,
                      7,
                      8,
                      9,
                      10,
                      11,
                      12,
                      13,
                      14,
                      15]
            --no_ack=True
            --rts_cts=2436
            --ur_count=3
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__mac_address = None
        self.__mcs = None
        self.__ht_mcs = None
        self.__no_ack = None
        self.__rts_cts = None
        self.__ur_count = None

    def reset_mac_parameters(self):
        self.__mac_address = None
        self.__mcs = None
        self.__ht_mcs = None
        self.__no_ack = None
        self.__rts_cts = None
        self.__ur_count = None

    def apply_tx_policy(self):
        # Check if a MAC address is set
        if self.mac_address is not None:
            for block in self.blocks():
                # Check block band to apply the MCS
                if block.band == BT_HT20:
                    # Checking at least one of the parameters is set
                    if self.ht_mcs is not None or self.no_ack is not None or self.rts_cts is not None or self.ur_count is not None:
                        # Creating transmission policy
                        tx_policy = block.tx_policies[self.mac_address]

                        # Checking other parameters one by one
                        if self.mcs is not None:
                            tx_policy.mcs = self.mcs
                        if self.ht_mcs is not None:
                            tx_policy.ht_mcs = self.ht_mcs
                        if self.no_ack is not None:
                            tx_policy.no_ack = self.no_ack
                        if self.rts_cts is not None:
                            tx_policy.rts_cts = self.rts_cts
                        if self.ur_count is not None:
                            tx_policy.ur_count = self.ur_count

                        self.log.debug("Block %s setting mac_address %s, mcs %s, ht_mcs %s, no_ack %s, rts_cts %s, and "
                                       "ur_count %s",
                                       block,
                                       str(self.mac_address),
                                       str(self.mcs),
                                       str(self.ht_mcs),
                                       str(self.no_ack),
                                       str(self.rts_cts),
                                       str(self.ur_count))
                    else:
                        self.log.debug("Not enough or invalid arguments, applying best-effort configuration!")
                else:
                    self.log.debug("WTP Block does not support ht_mcs, applying best-effort configuration!")
            # Resetting all params
            self.reset_mac_parameters()

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
    def config_tx_policy(self):
        """Return config_tx_policy."""

        return self.__config_tx_policy

    @config_tx_policy.setter
    def config_tx_policy(self, value):
        """Set config_tx_policy."""

        if value is not None:
            self.apply_tx_policy()

    @property
    def mac_address(self):
        """Return mac_address."""

        return self.__mac_address

    @mac_address.setter
    def mac_address(self, value):
        """Set mac_address."""
        if value is not None:
            if isinstance(value, str):
                self.__mac_address = EtherAddress(str(value))
            else:
                raise ValueError("Invalid value for mac_address!")
        else:
            self.__mac_address = None

    @property
    def mcs(self):
        """Return mcs."""

        return self.__mcs

    @mcs.setter
    def mcs(self, value):
        """Set mcs."""
        if value is not None:
            try:
                # TODO: verify the validity of this parameter
                self.__mcs = value  # Assuming it's an array of valid MCSes
            except TypeError:
                raise ValueError("Invalid value type for mcs, should be an integer!")

            if min(self.__mcs) < 0 or max(self.__mcs) > 54:
                raise ValueError("Invalid value range for mcs!")
        else:
            self.__mcs = None

    @property
    def ht_mcs(self):
        """Return ht_mcs."""

        return self.__ht_mcs

    @ht_mcs.setter
    def ht_mcs(self, value):
        """Set ht_mcs."""
        if value is not None:
            try:
                # TODO: verify the validity of this parameter
                self.__ht_mcs = value  # Assuming it's an array of valid MCSes
            except TypeError:
                raise ValueError("Invalid value type for ht_mcs, should be an integer!")

            if min(self.__ht_mcs) < 0 or max(self.__ht_mcs) > 15:
                raise ValueError("Invalid value range for ht_mcs!")
        else:
            self.__ht_mcs = None

    @property
    def no_ack(self):
        """Return no_ack."""

        return self.__no_ack

    @no_ack.setter
    def no_ack(self, value):
        """Set no_ack."""
        if value is not None:
            try:
                if value.lower() == 'true':
                    self.__no_ack = True
                else:
                    self.__no_ack = False
            except TypeError:
                raise ValueError("Invalid value type for no_ack, should be a boolean!")
        else:
            self.__no_ack = None

    @property
    def rts_cts(self):
        """Return rts_cts."""

        return self.__rts_cts

    @rts_cts.setter
    def rts_cts(self, value):
        """Set rts_cts."""
        if value is not None:
            try:
                self.__rts_cts = int(value)
            except TypeError:
                raise ValueError("Invalid value type for rts_cts, should be an integer between 0 and 2436!")

            if self.__rts_cts < 0 or self.__rts_cts > 2436:
                raise ValueError("Invalid value for rts_cts!")
        else:
            self.__rts_cts = None

    @property
    def ur_count(self):
        """Return ur_count."""

        return self.__ur_count

    @ur_count.setter
    def ur_count(self, value):
        """Set ur_count."""
        if value is not None:
            try:
                self.__ur_count = int(value)
            except TypeError:
                raise ValueError("Invalid value type for ur_count, should be an integer!")
        else:
            self.__ur_count = None


def launch(tenant_id, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return MACManager(tenant_id=tenant_id,
                      every=every)
