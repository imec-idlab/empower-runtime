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

"""NCQM Stats Handler APP"""

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_MONITORING_PERIOD
from empower.core.app import DEFAULT_PERIOD
import time


class NCQMStatsHandler(EmpowerApp):
    """NCQM Stats Handler APP

    Command Line Parameters:
        tenant_id: tenant id
        every: loop period in ms (optional, default 5000ms)

    Example:
        ./empower-runtime.py apps.handlers.ncqmstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__db_monitor = self.db_monitor
        self.__ncqm_stats_handler = {'message': 'NCQM stats handler is online!'}

    def wtp_up(self, wtp):
        for block in wtp.supports:
            # Calling NCQM stats
            self.ncqm(block=block,
                      every=DEFAULT_MONITORING_PERIOD,
                      callback=self.ncqm_stats_callback)

    def loop(self):
        """Periodic job."""
        if self.__db_monitor is not None:
            self.monitor.keep_last_measurements_only('ncqm_stats')

    def ncqm_stats_callback(self, ncqm_stats):
        """ New stats available. """
        crr_wtp_addr = str(ncqm_stats.block.addr)
        if crr_wtp_addr is not None:
            if self.__db_monitor is not None:
                ncqm = ncqm_stats.block.ncqm
                crr_timestamp_in_ms = int(round(time.time()))
                for unknown_ap in ncqm:
                    fields = ['WTP_ADDR', 'HIST_PACKETS', 'LAST_PACKETS',
                              'LAST_RSSI_AVG', 'LAST_RSSI_STD', 'MOV_RSSI',
                              'UNKNOWN_AP_ADDR']
                    values = [crr_wtp_addr, ncqm[unknown_ap]['hist_packets'], ncqm[unknown_ap]['last_packets'],
                              ncqm[unknown_ap]['last_rssi_avg'], ncqm[unknown_ap]['last_rssi_std'],
                              ncqm[unknown_ap]['mov_rssi'], str(unknown_ap)]

                    # Saving into db
                    self.monitor.insert_into_db(table='ncqm_stats',
                                                fields=fields,
                                                values=values,
                                                crr_timestamp_in_ms=crr_timestamp_in_ms)

    @property
    def ncqm_stats_handler(self):
        """Return default ncqm_stats_handler"""
        return self.__ncqm_stats_handler

    @ncqm_stats_handler.setter
    def ncqm_stats_handler(self, value):
        """Set ncqm_stats_handler"""
        self.__ncqm_stats_handler = value

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
        return self.__ncqm_stats_handler


def launch(tenant_id, db_monitor=None, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return NCQMStatsHandler(tenant_id=tenant_id, db_monitor=db_monitor, every=every)
