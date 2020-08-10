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

"""A MAC layer manager."""

# the manifest
MANIFEST = {
    "name": "empower.apps.managers.macmanager.macmanager",
    "desc": "A MAC layer manager REST API.",
    "params": {
        "tenant_id": {
            "desc": "The tenant on which this app must be loaded.",
            "mandatory": True,
            "type": "UUID"
        },
        "every": {
            "desc": "The control loop period (in ms).",
            "mandatory": False,
            "default": 5000,
            "type": "int"
        },
        "mac_address": {
            "desc": "MAC Address from the LVAP in which a transmission policy will be applied.",
            "mandatory": False,
            "default": None,
            "type": "string"
        },
        "no_ack": {
            "desc": "no_ack flag in which a transmission policy will apply.",
            "mandatory": False,
            "default": False,
            "type": "string"
        },
        "mcs": {
            "desc": "mcs in which a transmission policy will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "ht_mcs": {
            "desc": "ht_mcs in which a transmission policy will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "rts_cts": {
            "desc": "rts_cts in which a transmission policy will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "config_tx_policy": {
            "desc": "The flag used to start a flow, needs to be last argument.",
            "mandatory": True,
            "default": True,
            "type": "bool"
        }
    }
}