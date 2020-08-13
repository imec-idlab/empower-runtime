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

"""An Adaptive STA Manager."""

# the manifest
MANIFEST = {
    "name": "empower.apps.managers.adaptivestamanager.adaptivestamanager",
    "desc": "STA shaper manager REST API.",
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
        "minimum_bw": {
            "desc": "The minimum bandwidth that an STA should have (in Mbps).",
            "mandatory": False,
            "default": 0,
            "type": "int"
        },
        "maximum_bw": {
            "desc": "The maximum bandwidth that an STA should have (in Mbps).",
            "mandatory": False,
            "default": 100,
            "type": "int"
        },
        "bw_decrease_rate": {
            "desc": "The rate which the bandwidth shaper of the best effort STAs should be decreased (e.g., 0.2, 0.4).",
            "mandatory": False,
            "default": 0.2,
            "type": "int"
        },
        "bw_increase_rate": {
            "desc": "The rate which the bandwidth shaper of the best effort STAs should be increased (e.g., 0.2, 0.4).",
            "mandatory": False,
            "default": 0.2,
            "type": "int"
        },
        "active": {
            "desc": "The flag used to activate/deactivate adaptive shaping",
            "mandatory": True,
            "default": True,
            "type": "bool"
        }
    }
}