#!/usr/bin/env python3
#
# Copyright (c) 2019 Pedro Heleno Isolani
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
def format_slice_add_request(dscp, quantum, amsdu, scheduler):
    request = {
        "version": '1.0',
        "dscp": dscp,
        "lte": {
            "static-properties": {},
            "vbses": {}
        },
        "wifi": {
            "static-properties": {
                "quantum": str(quantum),
                "amsdu_aggregation": str(amsdu).lower(),
                "scheduler": str(scheduler)
            },
            "wtps": {}
        }
    }
    return request