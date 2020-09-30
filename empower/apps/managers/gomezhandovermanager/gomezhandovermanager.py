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

"""Gomez handover manager APP."""

from empower.core.app import EmpowerApp
from empower.main import RUNTIME
import statistics

DEFAULT_LONG_PERIOD = 20000


class GomezHandoverManager(EmpowerApp):
    """Gomez handover manager APP.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default 20000ms)

    Example:

        ./empower-runtime.py apps.managers.gomezhandovermanager.gomezhandovermanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__gomez_handover_manager = {
            'message': 'Gomez handover manager is online!',
            'wtps': {},
        }

        # Stats handlers
        self.__slice_stats_handler = None   # AP load
        self.__wifi_stats_handler = None    # Channel load
        self.__ucqm_stats_handler = None    # RSSIs
        self.__active = False
        self.__gomez_handover_manager['active'] = self.__active
        self.__avg_rssis = []
        self.__ap_loads = []

    def reset_all_params(self):
        self.__avg_rssis = []
        self.__ap_loads = []

    def handover_process(self):
        for lvap in self.lvaps():
            crr_lvap_addr = str(lvap.addr)
            best_block = None
            decision_factor = None
            for block in self.blocks():
                crr_wtp_addr = str(block.addr)

                # If sta within range...
                if crr_lvap_addr in self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps']:
                    wtp_sta_mean_rssi_dbm = \
                        self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['mov_rssi'][
                            'mean']
                    if decision_factor is None:
                        decision_factor = wtp_sta_mean_rssi_dbm * (
                                self.__gomez_handover_manager['wtps'][crr_wtp_addr]['throughput_mbps'] +
                                self.__gomez_handover_manager['wtps'][crr_wtp_addr]['channel_utilization'])
                        best_block = block
                    else:
                        new_decision_factor = wtp_sta_mean_rssi_dbm * (
                                self.__gomez_handover_manager['wtps'][crr_wtp_addr]['throughput_mbps'] +
                                self.__gomez_handover_manager['wtps'][crr_wtp_addr]['channel_utilization'])
                        # Compare
                        if new_decision_factor > decision_factor:
                            best_block = block

            self.log.debug("Triggering handover of LVAP: " + str(crr_lvap_addr) + " to AP: " + str(best_block))
            if lvap.blocks[0] is not None:
                lvap.blocks = best_block

    def loop(self):
        """Periodic job."""
        if self.__active:

            for wtp in self.wtps():
                self.add_wtp_structure(str(wtp.addr))

            # Step 1: get all metrics
            # Slice Stats
            if not self.get_slice_stats():
                return
            if not self.parse_slice_stats():
                return

            # Channel Utilization
            if not self.get_channel_load_stats():
                return
            if not self.parse_channel_stats():
                return

            # LVAP Stats (RSSI)
            if not self.get_ucqm_stats():
                return
            if not self.parse_ucqm_stats():
                return

            # LVAP Stats (Load)
            if not self.get_lvap_stats():
                return
            if not self.add_lvap_stats():
                return

            # Step 2: checking APs load
            for wtp in self.__gomez_handover_manager['wtps']:
                if self.__gomez_handover_manager['wtps'][wtp]['throughput_mbps'] is not None:
                    self.__ap_loads.append(self.__gomez_handover_manager['wtps'][wtp]['throughput_mbps'])

            for wtp in self.__gomez_handover_manager['wtps']:
                if self.__gomez_handover_manager['wtps'][wtp]['rssi']:
                    self.__avg_rssis.append(statistics.mean(self.__gomez_handover_manager['wtps'][wtp]['rssi']))

            handover_triggered = False
            if self.__ap_loads:
                # If Max(APLoads)-Min(APLoads)>Med(APLoads)
                if (max(self.__ap_loads) - min(self.__ap_loads)) > statistics.median(self.__ap_loads):
                    self.handover_process()
                    handover_triggered = True

            if not handover_triggered and self.__avg_rssis:
                # If Max(AvRSSIs)-Min(AvRSSIs)>Med(AvRSSIs)
                if (max(self.__avg_rssis) - min(self.__avg_rssis)) > statistics.median(self.__avg_rssis):
                    self.handover_process()

        # Reset all params for the next iteration
        self.reset_all_params()

    def add_wtp_structure(self, wtp_addr):
        self.__gomez_handover_manager['wtps'][wtp_addr] = {
            'throughput_mbps': None,
            'channel_utilization': None,
            'rssi': []
        }

    def get_slice_stats(self):
        if 'empower.apps.handlers.slicestatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__slice_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.slicestatshandler'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.slicestatshandler' is not online!")
            return False

    def parse_slice_stats(self):
        try:
            for wtp in self.__slice_stats_handler['wtps']:
                self.__gomez_handover_manager['wtps'][wtp]['throughput_mbps'] = \
                self.__slice_stats_handler['wtps'][wtp]['overall']['throughput_mbps']['mean']
        except:
            raise ValueError("APP 'empower.apps.handlers.slicestatshandler' is not parsed!")
            return False
        finally:
            return True

    def get_channel_load_stats(self):
        if 'empower.apps.handlers.wifistatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__wifi_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.wifistatshandler'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.wifistatshandler' is not online!")
            return False

    def parse_channel_stats(self):
        try:
            for wtp in self.__wifi_stats_handler['wtps']:
                self.__gomez_handover_manager['wtps'][wtp]['channel_utilization'] = \
                    self.__wifi_stats_handler['wtps'][wtp]['channel_utilization']['mean']
        except:
            raise ValueError("APP 'empower.apps.handlers.wifistatshandler' is not parsed!")
            return False
        finally:
            return True

    def get_ucqm_stats(self):
        # UCQM stats handler
        if 'empower.apps.handlers.ucqmstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__ucqm_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.ucqmstatshandler'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.ucqmstatshandler' is not online!")
            return False

    def parse_ucqm_stats(self):
        try:
            for lvap in self.lvaps():
                crr_lvap_addr = str(lvap.addr)
                if lvap.blocks[0] is not None:
                    crr_wtp_addr = str(lvap.blocks[0].addr)
                    wtp_sta_mean_rssi_dbm = \
                    self.__ucqm_stats_handler['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['mov_rssi']['mean']
                    if wtp_sta_mean_rssi_dbm is not None:
                        self.__gomez_handover_manager['wtps'][crr_wtp_addr]['rssi'].append(wtp_sta_mean_rssi_dbm)
        except:
            raise ValueError("APP 'empower.apps.handlers.ucqmstatshandler' is not parsed!")
            return False
        finally:
            return True

    def get_lvap_stats(self):
        if 'empower.apps.handlers.binstatshandler' in RUNTIME.tenants[self.tenant_id].components:
            self.__lvap_stats_handler = RUNTIME.tenants[self.tenant_id].components[
                'empower.apps.handlers.binstatshandler'].to_dict()
            return True
        else:
            raise ValueError("APP 'empower.apps.handlers.binstatshandler' is not online!")
            return False

    def add_lvap_stats(self):
        # Getting LVAPs load and filling the structure
        for lvap in self.lvaps():
            crr_lvap_addr = str(lvap.addr)
            if lvap.blocks[0] is not None:
                crr_wtp_addr = str(lvap.blocks[0].addr)
                if crr_wtp_addr in self.__gomez_handover_manager['wtps']:
                    if crr_lvap_addr in self.__lvap_stats_handler['lvaps']:
                        lvap_mean_throughput_mbps = \
                            self.__lvap_stats_handler['lvaps'][crr_lvap_addr]['rx_throughput_mbps']['mean']
                        if lvap_mean_throughput_mbps is not None:
                            self.__gomez_handover_manager['wtps'][crr_wtp_addr]['throughput_mbps'] += lvap_mean_throughput_mbps
                    else:
                        raise ValueError("LVAP is not yet present in lvapstatshandler dictionary!")
                        return False
                else:
                    raise ValueError("WTP is not yet present in gomez_handover_manager dictionary!")
                    return False
        return True

        # Now filling the MCDA matrix structure
        for crr_wtp_addr in self.__mcda_handover_manager['wtps']:
            for crr_lvap_addr in self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps']:
                self.__mcda_handover_manager['wtps'][crr_wtp_addr]['lvaps'][crr_lvap_addr]['metrics']['values'][
                    crr_criteria_index] += wtps_load[crr_wtp_addr]    # sum of all LVAP load



    @property
    def slice_stats_handler(self):
        """Return default slice_stats_handler"""
        return self.__slice_stats_handler

    @slice_stats_handler.setter
    def slice_stats_handler(self, value):
        """Set slice_stats_handler"""
        self.__slice_stats_handler = value

    @property
    def wifi_stats_handler(self):
        """Return default wifi_stats_handler"""
        return self.__wifi_stats_handler

    @wifi_stats_handler.setter
    def wifi_stats_handler(self, value):
        """Set wifi_stats_handler"""
        self.__wifi_stats_handler = value

    @property
    def ucqm_stats_handler(self):
        """Return default ucqm_stats_handler"""
        return self.__ucqm_stats_handler

    @ucqm_stats_handler.setter
    def ucqm_stats_handler(self, value):
        """Set ucqm_stats_handler"""
        self.__ucqm_stats_handler = value

    @property
    def active(self):
        """Return active."""
        return self.__active

    @active.setter
    def active(self, value):
        """Set active."""
        self.__active = value

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
        self.__gomez_handover_manager['active'] = self.__active
        return self.__gomez_handover_manager


def launch(tenant_id,
           every=DEFAULT_LONG_PERIOD):
    """ Initialize the module. """

    return GomezHandoverManager(tenant_id=tenant_id,
                                every=every)
