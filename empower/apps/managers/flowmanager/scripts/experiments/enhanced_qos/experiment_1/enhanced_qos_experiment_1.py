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


print("Advertising Flow 1...")
# Advertise flow 1
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_1/flow1.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")
print("Now start the flow from the RPI 1 - mgen input flow1.mgn! (click must be running there)")

print("Sleeping...")
time.sleep(30)

print("Advertising Flow 2...")
# Advertise flow 2
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_1/flow2.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")
print("Now start the flow from the RPI 2 - mgen input flow2.mgn! (click must be running there)")

print("Sleeping...")
time.sleep(30)

print("Advertising Flow 3...")
# Advertise flow 3
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_1/flow3.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")
print("Now start the flow from the RPI 3 - mgen input flow3.mgn! (click must be running there)")

print("Sleeping...")
time.sleep(30)

print("Advertising and running Flow 4...")
# Advertise flow 3
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_1/flow4.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(30)

print("Advertising Flow 5...")
# Advertise flow 3
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_1/flow5.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(30)

print("Advertising Flow 6...")
# Advertise flow 3
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_1/flow6.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")