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
import ipaddress
import socket
import threading


class LVAPManager(EmpowerApp):
    """LVAP Manager App

    Command Line Parameters:
        tenant_id: tenant id

    Example:
        ./empower-runtime.py apps.managers.lvapmanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lvap_manager = {"message": "LVAP Manager is online!"}
        self.__ip_addr = None
        self.__port = None
        self.__bw_shaper = None
        self.__dl_shaper = None

    def reset_lvap_parameters(self):
        self.__ip_addr = None
        self.__port = None
        self.__bw_shaper = None
        self.__dl_shaper = None

    def send_config_to_lvap(self):
        if self.__ip_addr is not None and self.__port is not None:
            thread = threading.Thread(target=self.open_socket)
            thread.daemon = True
            thread.start()
        else:
            self.log.debug("IP address or port is not set, aborting configuration!")

    def open_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((str(self.__ip_addr), self.__port))
            cmd = "WRITE "
            if self.__bw_shaper is not None:
                cmd_bw_shaper = cmd + "bw_shaper.rate " + str(self.__bw_shaper) + "\n"
                s.sendall(cmd_bw_shaper.encode())
                data = s.recv(1024)
                self.log.debug("Sending new configurations to LVAP" + str(repr(data)))
            if self.__dl_shaper is not None:
                cmd_bw_shaper = cmd + "dl_shaper.delay " + str(self.__dl_shaper) + "\n"
                s.sendall(cmd_bw_shaper.encode())
                data = s.recv(1024)
                self.log.debug("Sending new configurations to LVAP" + str(repr(data)))
        self.reset_lvap_parameters()

    @property
    def ip_addr(self):
        """Return ip_addr"""
        return self.__ip_addr

    @ip_addr.setter
    def ip_addr(self, value):
        """Set ip_addr"""
        try:
            self.__ip_addr = ipaddress.IPv4Address(str(value))
        except:
            raise ValueError("Invalid value for IPv4 address!")
            self.__ip_addr = None

    @property
    def port(self):
        """Return port"""
        return self.__port

    @port.setter
    def port(self, value):
        """Set port"""
        if isinstance(value, int):
            if value > 0:
                self.__port = value
            else:
                self.reset_lvap_parameters()
                raise ValueError("Invalid value for port, port needs to be greater than 0!")
        else:
            self.reset_lvap_parameters()
            raise ValueError("Invalid value type for port, integer required!")

    @property
    def bw_shaper(self):
        """Return bw_shaper"""
        return self.__bw_shaper

    @bw_shaper.setter
    def bw_shaper(self, value):
        """Set bw_shaper"""
        if isinstance(value, int):
            if value >= 0:
                self.__bw_shaper = value
            else:
                self.reset_lvap_parameters()
                raise ValueError("Invalid value for bw_shaper, bw_shaper needs to be greater than or equal to 0!")
        else:
            self.reset_lvap_parameters()
            raise ValueError("Invalid value type for bw_shaper, integer required!")

    @property
    def dl_shaper(self):
        """Return dl_shaper"""
        return self.__dl_shaper

    @dl_shaper.setter
    def dl_shaper(self, value):
        """Set dl_shaper"""
        if isinstance(value, int):
            if value >= 0:
                self.__dl_shaper = value
            else:
                self.reset_lvap_parameters()
                raise ValueError("Invalid value for dl_shaper, bw_shaper needs to be greater than or equal to 0!")
        else:
            self.reset_lvap_parameters()
            raise ValueError("Invalid value type for dl_shaper, integer required!")

    @property
    def config_lvap(self):
        """Return config_slice."""
        return self.__config_slice

    @config_lvap.setter
    def config_lvap(self, value):
        """Set config_lvap."""
        if value is not None:
            self.send_config_to_lvap()

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


def launch(tenant_id):
    """ Initialize the module. """

    return LVAPManager(tenant_id=tenant_id)
