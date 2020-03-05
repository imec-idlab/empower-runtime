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

"""WiFi Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD


class WiFiStatsHandler(EmpowerApp):
    """WiFi Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.wifistatshandler.wifistatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__wifi_stats_handler = {'network_channel_quality_map': {},
                                     'user_channel_quality_map': {}}

    def loop(self):
        """Periodic job."""
        self.log.debug('WiFi Stats Handler APP Loop...')
        for wtp in self.wtps():
            for block in wtp.supports:
                # Calling wifi stats
                self.ncqm(block=block,
                          callback=self.ncqm_stats_callback)
                self.ucqm(block=block,
                          callback=self.ucqm_stats_callback)

    def ncqm_stats_callback(self, ncqm_stats):
        """ New stats available. """
        self.__wifi_stats_handler['network_channel_quality_map'] = ncqm_stats

    def ucqm_stats_callback(self, ucqm_stats):
        """ New stats available. """
        self.__wifi_stats_handler['user_channel_quality_map'] = ucqm_stats

    @property
    def wifi_stats_handler(self):
        """Return default wifi_stats_handler"""
        return self.__wifi_stats_handler

    @wifi_stats_handler.setter
    def wifi_stats_handler(self, value):
        """Set wifi_stats_handler"""
        self.__wifi_stats_handler = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__wifi_stats_handler


def launch(tenant_id, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return WiFiStatsHandler(tenant_id=tenant_id, every=every)
