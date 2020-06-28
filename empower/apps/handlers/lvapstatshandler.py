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

"""LVAP Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_MONITORING_PERIOD
from empower.core.app import DEFAULT_PERIOD


class LVAPStatsHandler(EmpowerApp):
    """LVAP Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        polling: polling frequency in ms (optional, default 1000ms)
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.lvapstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__lvap_stats_handler = {'message': 'LVAP stats handler is online!',
                                     'every': self.__every,
                                     'polling': self.__polling,
                                     'lvaps': {}}

    def loop(self):
        """Periodic job."""
        for lvap in self.lvaps():
            self.lvap_stats(lvap=lvap.addr,
                            every=self.__polling,
                            callback=self.lvap_stats_callback)

            if lvap.blocks[0] is not None:
                associated_wtp_addr = lvap.blocks[0].addr
                if self.__db_monitor is not None:
                    fields = ['LVAP_ADDR', 'WTP_ADDR', 'FLAG']
                    values = [str(lvap.addr), str(associated_wtp_addr), 1]

                    # Saving into db
                    self.monitor.insert_into_db(table='lvap_association_stats', fields=fields, values=values)

        if self.__db_monitor is not None:
            self.monitor.keep_last_measurements_only(table='lvap_stats')

    def lvap_stats_callback(self, lvap_stats):
        """ New stats available. """
        crr_lvap_addr = str(lvap_stats.to_dict()['lvap'])
        if crr_lvap_addr not in self.__lvap_stats_handler['lvaps']:
            self.__lvap_stats_handler['lvaps'][crr_lvap_addr] = {}

        self.__lvap_stats_handler['lvaps'][crr_lvap_addr] = lvap_stats.to_dict()
        if self.__db_monitor is not None:
            fields = ['LVAP_ADDR', 'BEST_MCS_PROB']
            values = [crr_lvap_addr, self.__lvap_stats_handler['lvaps'][crr_lvap_addr]['best_prob']]

            # Saving into db
            self.monitor.insert_into_db(table='lvap_stats', fields=fields, values=values)

    @property
    def lvap_stats_handler(self):
        """Return default lvap_stats_handler"""
        return self.__lvap_stats_handler

    @lvap_stats_handler.setter
    def lvap_stats_handler(self, value):
        """Set lvap_stats_handler"""
        self.__lvap_stats_handler = value

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
    def polling(self):
        """Return polling period."""
        return self.__polling

    @polling.setter
    def polling(self, value):
        """Set polling period."""
        self.__polling = int(value)

    @property
    def db_monitor(self):
        """Return db_monitor"""
        return self.__db_monitor

    @db_monitor.setter
    def db_monitor(self, value):
        """Set db_monitor"""
        if value is not None:
            self.__db_monitor = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        self.__lvap_stats_handler['every'] = self.__every
        self.__lvap_stats_handler['polling'] = self.__polling
        return self.__lvap_stats_handler


def launch(tenant_id, db_monitor=None, polling=DEFAULT_MONITORING_PERIOD, every=DEFAULT_MONITORING_PERIOD):
    """ Initialize the module. """

    return LVAPStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, polling=polling, every=every)
