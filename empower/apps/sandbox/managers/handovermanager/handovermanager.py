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

"""Sandbox Handover Manager APP."""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD


class HandoverManager(EmpowerApp):
    """Sandbox Handover Manager APP.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:

        ./empower-runtime.py apps.sandbox.managers.handovermanager.handovermanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__wifi_handover_manager = {"message": "Sandbox handover Manager is online!"}
        self.__WTP_LVAP_map = {"00:0D:B9:42:6A:00": {"LVAPs": ["DC:A6:32:65:E7:AA",
                                                               "DC:A6:32:0A:E1:D4"]},
                               "00:0D:B9:42:72:08": {"LVAPs": ["DC:A6:32:0A:E0:C9",
                                                               "DC:A6:32:0A:B8:22"]}}

    def loop(self):
        """Periodic job."""
        # self.log.debug("Sandbox handover Manager APP loop...")
        # For all blocks in all APs
        for block in self.blocks():
            # If there is a static configuration in the map
            if str(block.addr) in self.__WTP_LVAP_map:
                # For all clients connected...
                for lvap in self.lvaps():
                    # If there is a static placement for the station
                    if str(lvap.addr) in self.__WTP_LVAP_map[str(block.addr)]["LVAPs"]:
                        # If the station is not connected to the defined static configuration: do handover
                        if str(lvap.blocks[0].addr) != str(block.addr):
                            self.log.info("Sandbox handover triggered!")
                            lvap.blocks = block

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

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__wifi_handover_manager


def launch(tenant_id,
           every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return HandoverManager(tenant_id=tenant_id,
                           every=every)

