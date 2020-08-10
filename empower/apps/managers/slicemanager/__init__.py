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

"""A Slice manager."""

# the manifest
MANIFEST = {
    "name": "empower.apps.managers.slicemanager.slicemanager",
    "desc": "A slice manager REST API.",
    "params": {
        "tenant_id": {
            "desc": "The tenant on which this app must be loaded.",
            "mandatory": True,
            "type": "UUID"
        },
        "dscp": {
            "desc": "The DSCP from the slice in which a configuration will be applied.",
            "mandatory": True,
            "default": None,
            "type": "string"
        },
        "amsdu": {
            "desc": "The amsdu aggregation the slice will apply.",
            "mandatory": False,
            "default": False,
            "type": "bool"
        },
        "quantum": {
            "desc": "The quantum that the slice will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "scheduler": {
            "desc": "The scheduler that the slice will apply.",
            "mandatory": False,
            "default": None,
            "type": "int"
        },
        "wtp_addr": {
            "desc": "The specific WTP address from which the slice configuration will be applied.",
            "mandatory": False,
            "default": None,
            "type": "string"
        },
        "config_slice": {
            "desc": "The flag used to configs a slice, needs to be last argument.",
            "mandatory": True,
            "default": True,
            "type": "bool"
        }
    }
}