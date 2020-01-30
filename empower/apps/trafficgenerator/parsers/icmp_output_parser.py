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

import re
import time


def read_icmp_output(crr_process, append):
    for line in iter(crr_process.stdout.readline, ""):
        if line:
            # Process PING lines
            crr_latency = {'timestamp': None,
                           'unit': 'ms',
                           'value': None}
            tmp_line = re.split(' |=', str(line, 'utf-8').replace('\n', ''))
            if 'PING' not in tmp_line and '' not in tmp_line:
                crr_latency['timestamp'] = time.time()
                if 'timeout' not in tmp_line and 'Unreachable' not in tmp_line and 'icmp_seq' in tmp_line:
                    crr_latency['unit'] = tmp_line[10]
                    crr_latency['value'] = float(tmp_line[9])
            append(crr_latency)