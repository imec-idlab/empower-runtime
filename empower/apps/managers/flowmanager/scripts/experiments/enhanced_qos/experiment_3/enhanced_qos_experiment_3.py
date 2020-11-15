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
import os

# Experimentation parameters and values
parser = OptionParser()
parser.add_option("", "--controller_ip", type="string", default="143.129.76.37")  # Empower controller (sandbox)
parser.add_option("", "--tenant_id", type="string", default="8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719")  # sandbox
parser.add_option("", "--user", type="string", default="root")  # e.g., root, user
parser.add_option("", "--password", type="string", default="root")  # e.g., root, password
(options, args) = parser.parse_args()

print("Trying to activate Gomez approach..")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/activate.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.gomezhandovermanager.gomezhandovermanager']
call(curl_terminal_command)
print("Done!")

print("Trying to activate our user association algorithm (MCDA)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/activate.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.mcdahandovermanager.fullmcdahandovermanager']
call(curl_terminal_command)
print("Done!")

os.system("say Event 1 second 10")
print("Event 1 (sec 10)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow5.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow6.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(60)

os.system("say Event 2 second 70")
print("Event 2 (sec 70)...")
os.system("say Start 20Mbps flow on RPI 1 and 3!")
print("Start 20Mbps flow on RPI 1 and 3!")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow1.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow3.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(60)

os.system("say Event 3 second 130")
print("Event 3 (sec 130)...")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow5_stop.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow6_stop.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Sleeping...")
time.sleep(60)

os.system("say Event 4 second 190...")
os.system("say Start a 10Mbps flow on RPI 2!")
print("Event 4 (sec 190)...")
print("Start a 10Mbps flow on RPI 2!")
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow5_mod.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow6_mod.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow4.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/experiment_3/flow2.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

os.system("say Now just wait some minutes...")