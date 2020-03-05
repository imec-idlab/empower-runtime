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

"""Bin Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD


class BinStatsHandler(EmpowerApp):
    """Bin Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.binstatshandler.binstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__bin_stats_handler = {}

    def loop(self):
        """Periodic job."""
        self.log.debug('Bin Stats Handler APP Loop...')
        for lvap in self.lvaps():
            # Calling bin counter for each LVAP
            self.bin_counter(lvap=lvap.addr,
                             callback=self.bin_stats_callback)

    def bin_stats_callback(self, bin_stats):
        """ New stats available. """
        self.__bin_stats_handler[str(bin_stats.to_dict()['lvap'])] = bin_stats.to_dict()
        self.log.debug(bin_stats.to_dict())

    @property
    def bin_stats_handler(self):
        """Return default bin_stats_handler"""
        return self.__bin_stats_handler

    @bin_stats_handler.setter
    def bin_stats_handler(self, value):
        """Set bin_stats_handler"""
        self.__bin_stats_handler = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__bin_stats_handler


def launch(tenant_id, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return BinStatsHandler(tenant_id=tenant_id, every=every)