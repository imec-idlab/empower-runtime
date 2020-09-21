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

"""LVAP Manager App."""

from empower.core.app import EmpowerApp
import socket
import threading
from empower.core.app import DEFAULT_PERIOD


class UplinkStatsManager(EmpowerApp):
    """Uplink Stats Manager App

    Command Line Parameters:
        tenant_id: tenant id

    Example:
        ./empower-runtime.py empower.apps.handlers.uplinkstatshandler \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lvap_manager = {
            "message": "Uplink Stats Manager is online!",
            "lvaps": {
                'DC:A6:32:65:E7:AA': {
                    'ip_addr': '192.168.2.21',
                    'queueing_delay': None
                },
                # 'DC:A6:32:0A:E1:D4': {
                #     'ip_addr': '192.168.2.22',
                #     'queueing_delay': None
                # },
                # 'DC:A6:32:0A:E0:C9': {
                #     'ip_addr': '192.168.2.23',
                #     'queueing_delay': None
                # },
                # 'DC:A6:32:0A:B8:22': {
                #     'ip_addr': '192.168.2.24',
                #     'queueing_delay': None
                # },
                # '00:00:00:00:00:00': {
                #     'ip_addr': '192.168.2.25',
                #     'queueing_delay': None
                # },
                # '00:00:00:00:00:00': {
                #     'ip_addr': '192.168.2.26',
                #     'queueing_delay': None
                # }
            }
        }

    def loop(self):
        """Periodic job."""
        for lvap in self.lvaps():
            crr_lvap_addr = str(lvap.addr)
            if crr_lvap_addr in self.__lvap_manager['lvaps']:
                # TODO: create a function with a thread for each lvap
                self.get_config_from_lvap(crr_lvap_addr)

                if self.__db_monitor is not None:
                    fields = ['LVAP_ADDR', 'QUEUEING_DELAY_MS']
                    addr = crr_lvap_addr
                    queueing_delay = self.__lvap_manager['lvaps'][crr_lvap_addr]['queueing_delay']
                    values = [addr, queueing_delay]

                    # Saving into db
                    self.monitor.insert_into_db(table='lvap_delay_stats', fields=fields, values=values)

        if self.__db_monitor is not None:
            self.monitor.keep_last_measurements_only(table='lvap_delay_stats')

    def get_config_from_lvap(self, crr_lvap_addr):
        # TODO: get config from lvap (thread)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect(self.__lvap_manager['lvaps'][crr_lvap_addr]['ip_addr'], 7777)
                cmd = "READ infobase.delay"
                s.sendall(cmd.encode())
                data = s.recv(1024)
                self.log.debug("Requesting data from LVAP")
                queueing_delay = data.decode()[3]
                self.__lvap_manager['lvaps'][crr_lvap_addr]['queueing_delay'] = queueing_delay
        except:
            self.__lvap_manager['lvaps'][crr_lvap_addr]['queueing_delay'] = None
            raise ValueError("Timeout requesting delay stats from LVAP")

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
    def lvap_manager(self):
        """Return default LVAP Manager"""
        return self.__lvap_manager

    @lvap_manager.setter
    def lvap_manager(self, value):
        """Set WiFi LVAP Manager"""
        self.__lvap_manager = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__lvap_manager


def launch(tenant_id, every=DEFAULT_PERIOD):
    """ Initialize the module. """

    return UplinkStatsManager(tenant_id=tenant_id, every=every)