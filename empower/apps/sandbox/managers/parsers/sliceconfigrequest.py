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


# No WTPs options for now
def format_slice_config_request(tenant_id, dscp, default_quantum, default_amsdu=False, default_scheduler=0, wtps=None):
    request = {
        "version": "1.0",
        "tenant_id": str(tenant_id),
        "dscp": dscp,
        "lte": {
            "static-properties": {},
            "vbses": {}
        },
        "wifi": {
            "static-properties": {
                "quantum": str(default_quantum),
                "amsdu_aggregation": str(default_amsdu).lower(),
                "scheduler": str(default_scheduler)
            },
            "wtps": {}
        }
    }

    if wtps is not None:
        for wtp in wtps:
            request["wifi"]["wtps"][str(wtp["addr"])] = {
                "static-properties": {
                    "quantum": str(wtp["quantum"]),
                    "amsdu_aggregation": str(wtp["amsdu_aggregation"]).lower(),
                    "scheduler": str(wtp["scheduler"])
                }
            }
    return request
