#!/usr/bin/env python3
#
# Copyright (c) 2018 Pedro Heleno Isolani
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

"""An LVAP manager."""

# the manifest
MANIFEST = {
    "name": "empower.apps.managers.lvapmanager.lvapmanager",
    "desc": "A LVAP manager REST API.",
    "params": {
        "tenant_id": {
            "desc": "The tenant on which this app must be loaded.",
            "mandatory": True,
            "type": "UUID"
        },
        "ip_addr": {
            "desc": "The IP address from the LVAP in which a configuration will be applied.",
            "mandatory": True,
            "default": None,
            "type": "string"
        },
        "port": {
            "desc": "The port the LVAP is listening to.",
            "mandatory": True,
            "default": False,
            "type": "int"
        },
        "bw_shaper": {
            "desc": "The bandwidth shaper value for uplink in B/s in which the LVAP will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "dl_shaper": {
            "desc": "The delay shaper value for uplink in seconds in which the LVAP will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "config_lvap": {
            "desc": "The flag used to configs a LVAP, needs to be last argument.",
            "mandatory": True,
            "default": True,
            "type": "bool"
        }
    }
}