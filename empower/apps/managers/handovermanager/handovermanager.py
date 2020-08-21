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

"""Handover Manager APP."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD


class HandoverManager(EmpowerApp):
    """Handover Manager APP.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.managers.handovermanager.handovermanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__wifi_handover_manager = {"message": "Handover Manager is online!"}
        self.__wtp_addr = None
        self.__lvap_addr = None

    def reset_parameters(self):
        self.__wtp_addr = None
        self.__lvap_addr = None

    def do_handover(self):
        # For all blocks in all APs
        for block in self.blocks():
            # If there is a static configuration in the map
            if str(block.addr) == self.__wtp_addr:
                # For all clients connected...
                for lvap in self.lvaps():
                    # If there is a static placement for the station
                    if str(lvap.addr) == self.__lvap_addr:
                        if lvap.blocks[0] is not None:
                            # If the station is not connected: do handover
                            if str(lvap.blocks[0].addr) != str(block.addr):
                                self.log.info("Handover triggered!")
                                lvap.blocks = block
        self.reset_parameters()

    @property
    def lvap_addr(self):
        """Return lvap_addr"""
        return self.__lvap_addr

    @lvap_addr.setter
    def lvap_addr(self, value):
        """Set lvap_addr"""
        self.__lvap_addr = value

    @property
    def wtp_addr(self):
        """Return wtp_addr"""
        return self.__wtp_addr

    @wtp_addr.setter
    def wtp_addr(self, value):
        """Set wtp_addr"""
        self.__wtp_addr = value

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
    def config_handover(self):
        """Return config_handover."""
        return self.config_handover

    @config_handover.setter
    def config_handover(self, value):
        """Set config_handover."""
        if value is not None:
            self.do_handover()

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__wifi_handover_manager


def launch(tenant_id,
           every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return HandoverManager(tenant_id=tenant_id,
                           every=every)

