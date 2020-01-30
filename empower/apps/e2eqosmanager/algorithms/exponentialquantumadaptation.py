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

KEEP_CONFIGURATION = 0
EXPLOITATION = 1
EXPLORATION = 2

""" Simple Exponential Quantum Adaptation using different adaptation rates for Exploitation and Exploration """


class ExponentialQuantumAdaptation:

    def __init__(self,
                 exploration_rate=0.05, exploration_trigger=5,
                 exploitation_rate=0.20, exploitation_trigger=1,
                 min_quantum=200):

        self.exploration_rate = exploration_rate  # % to increase BE quantum
        self.exploitation_rate = exploitation_rate  # % to decrease BE quantum

        self.exploration_trigger = exploration_trigger  # int to represent when to increase BE quantum
        self.exploitation_trigger = exploitation_trigger  # int to represent when to decrease BE quantum

        self.exploration_counter = 0  # int to trigger exploration
        self.exploitation_counter = 0  # int to trigger exploitation

        self.min_quantum = min_quantum

        self.status = KEEP_CONFIGURATION

    def exploit(self):
        self.exploitation_counter += 1
        if self.exploitation_counter >= self.exploitation_trigger:
            self.status = EXPLOITATION
            self.exploitation_counter = 0

    def explore(self):
        self.exploration_counter += 1
        if self.exploration_counter >= self.exploration_trigger:
            self.status = EXPLORATION
            self.exploration_counter = 0

    def get_new_quantum(self, old_quantum):
        if self.status == EXPLORATION:
            new_quantum = int(old_quantum + (old_quantum * self.exploration_rate))
        elif self.status == EXPLOITATION:
            new_quantum = int(old_quantum - (old_quantum * self.exploitation_rate))
            if new_quantum < self.min_quantum:
                new_quantum = self.min_quantum
        else:
            new_quantum = int(old_quantum)
        self.status = KEEP_CONFIGURATION
        return new_quantum

    def __str__(self):
        return "Exploitation rate: " + str(self.exploitation_rate) + \
               " trigger: " + str(self.exploitation_trigger) + \
               " counter: " + str(self.exploitation_counter) + \
               "Exploration rate:" + str(self.exploration_rate) + \
               " trigger: " + str(self.exploration_trigger) + \
               " counter: " + str(self.exploration_counter)
