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

"""Slice Manager App."""

from empower.core.app import EmpowerApp
from empower.datatypes.dscp import DSCP

from empower.apps.managers.parsers.sliceconfigrequest import *


class SliceManager(EmpowerApp):
    """Slice Manager App

    Command Line Parameters:
        tenant_id: tenant id

    Example:
        ./empower-runtime.py apps.managers.slicemanager \
            --tenant_id=52313ecb-9d00-4b7d-b873-b55d3d9ada26D
            /
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__slice_manager = {"message": "Slice Manager is online!"}
        self.__dscp = None
        self.__quantum = None

    def send_slice_config_to_wtp(self):
        if self.__dscp is not None and self.__quantum is not None:
            new_slice = format_slice_config_request(tenant_id=self.tenant_id,
                                                    dscp=self.__dscp,
                                                    default_quantum=self.__new_quantum)
            self.log.debug("Sending new slice configurations to APs")
            self.tenant.set_slice(self.__dscp, new_slice)
        else:
            self.log.debug("DSCP or quantum is not set, aborting configuration!")

    @property
    def dscp(self):
        """Return dscp"""
        return self.__dscp

    @dscp.setter
    def dscp(self, value):
        """Set DSCP"""
        try:
            self.__dscp = DSCP(value)
        except:
            raise ValueError("Invalid value for dscp!")
            self.__dscp = None

    @property
    def quantum(self):
        """Return quantum"""
        return self.__quantum

    @quantum.setter
    def quantum(self, value):
        """Set quantum"""
        if isinstance(value, int):
            if value > 0:
                self.__quantum = value
                self.send_slice_config_to_wtp()
            else:
                raise ValueError("Invalid value for quantum, quantum needs to be greater than 0!")
                self.__dscp = None
        else:
            raise ValueError("Invalid value type for quantum, integer required!")
            self.__dscp = None

    @property
    def slice_manager(self):
        """Return default Slice Manager"""
        return self.__slice_manager

    @slice_manager.setter
    def slice_manager(self, value):
        """Set WiFi Slice Manager"""
        self.__slice_manager = value

    def to_dict(self):
        """ Return a JSON-serializable."""
        return self.__slice_manager


def launch(tenant_id):
    """ Initialize the module. """

    return SliceManager(tenant_id=tenant_id)
