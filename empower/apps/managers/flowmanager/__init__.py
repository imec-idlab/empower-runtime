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

"""A Flow manager APP."""

# the manifest
MANIFEST = {
    "name": "empower.apps.managers.flowmanager.flowmanager",
    "desc": "A Flow manager REST API.",
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
        "flow_id": {
            "desc": "The ID of the flow.",
            "mandatory": True,
            "default": None,
            "type": "int"
        },
        "flow_type": {
            "desc": "The type of the flow, BE or QoS.",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_dscp": {
            "desc": "The DSCP in which the flow is going to belong to.",
            "mandatory": False,
            "default": None,
            "type": "str"
        },
        "flow_protocol": {
            "desc": "The IP protocol used.",
            "mandatory": True,
            "default": "UDP",
            "type": "str"
        },
        "flow_distribution": {
            "desc": "The flow distribution.",
            "mandatory": False,
            "default": "PERIODIC",
            "type": "str"
        },
        "flow_frame_size": {
            "desc": "The frame size of the flow.",
            "mandatory": False,
            "default": 1024,
            "type": "int"
        },
        "flow_bw_req_mbps": {
            "desc": "The bandwidth requirements of the flow (Mbps)",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_delay_req_ms": {
            "desc": "The delay requirements of the flow (ms)",
            "mandatory": False,
            "default": None,
            "type": "str"
        },
        "flow_src_ip_addr": {
            "desc": "The IP address of the source.",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_dst_ip_addr": {
            "desc": "The IP address of the destination.",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_src_mac_addr": {
            "desc": "The MAC address of the source.",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_dst_mac_addr": {
            "desc": "The MAC address of the destination.",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_dst_port": {
            "desc": "The port of the destination.",
            "mandatory": True,
            "default": None,
            "type": "str"
        },
        "flow_duration": {
            "desc": "The duration of the flow.",
            "mandatory": True,
            "default": 30,
            "type": "int"
        },
        "start_flow": {
            "desc": "The flag used to start a flow, needs to be last argument.",
            "mandatory": False,
            "default": True,
            "type": "bool"
        }
    }
}