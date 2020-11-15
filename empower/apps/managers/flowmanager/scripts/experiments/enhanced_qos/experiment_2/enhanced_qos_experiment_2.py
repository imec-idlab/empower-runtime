#!/usr/bin/env python
__author__ = "Pedro Heleno Isolani"
__copyright__ = "Copyright 2020, The SDN WiFi MAC Manager"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Pedro Heleno Isolani"
__email__ = "pedro.isolani@uantwerpen.be"
__status__ = "Prototype"

from subprocess import call
from optparse import OptionParser
import time
import paramiko
from scp import SCPClient

# Experimentation parameters and values
parser = OptionParser()
parser.add_option("", "--controller_ip", type="string", default="143.129.76.37")  # Empower controller (sandbox)
parser.add_option("", "--tenant_id", type="string", default="8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719")  # sandbox
parser.add_option("", "--user", type="string", default="root")  # e.g., root, user
parser.add_option("", "--password", type="string", default="root")  # e.g., root, password
(options, args) = parser.parse_args()

print("Trying to activate Gomez approach..")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/activate.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.gomezhandovermanager.gomezhandovermanager']
call(curl_terminal_command)
print("Done!")

print("Trying to activate our user association algorithm (MCDA)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/activate.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.mcdahandovermanager.fullmcdahandovermanager']
call(curl_terminal_command)
print("Done!")

print("Event 1 (sec 10)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow3.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow4.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(60)

print("Event 2 (sec 70)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow2.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow5.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(60)

print("Event 3 (sec 130)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow3_stop.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow4_stop.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(60)

print("Event 4 (sec 190)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow3_mod.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow4_mod.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow1.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_2/flow6.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")