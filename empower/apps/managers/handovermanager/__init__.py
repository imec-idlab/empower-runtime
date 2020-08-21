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

"""A handover manager."""

# the manifest
MANIFEST = {
    "name": "empower.apps.managers.handovermanager.handovermanager",
    "desc": "A handover manager REST API.",
    "params": {
        "tenant_id": {
            "desc": "The tenant on which this app must be loaded.",
            "mandatory": True,
            "type": "UUID"
        },
        "lvap_addr": {
            "desc": "The MAC address of the LVAP in which a handover will be applied.",
            "mandatory": True,
            "default": None,
            "type": "string"
        },
        "wtp_addr": {
            "desc": "The MAC address of the new WTP.",
            "mandatory": True,
            "default": None,
            "type": "string"
        },
        "config_handover": {
            "desc": "The flag used to do the handover, needs to be last argument.",
            "mandatory": True,
            "default": True,
            "type": "bool"
        }
    }
}