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

# Experimentation parameters and values
parser = OptionParser()
parser.add_option("", "--controller_ip", type="string", default="10.11.17.1")  # Empower controller (wilabt)
#parser.add_option("", "--controller_ip", type="string", default="146.175.219.129")  # Empower controller (sandbox)
parser.add_option("", "--tenant_id", type="string", default="f1160872-c9c6-4d7f-b7f7-3e4a01c62a90")  # wilabt
#parser.add_option("", "--tenant_id", type="string", default="8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719")  # sandbox
parser.add_option("", "--user", type="string", default="root")  # e.g., root, user
parser.add_option("", "--password", type="string", default="root")  # e.g., root, password

(options, args) = parser.parse_args()

# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/wilabt/flow6.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)

# time.sleep(30)
#
# curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/wilabt/flow8.json',
#                          'http://' + str(options.user) + ':' + str(options.password) + '@' +
#                          str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
#                          '/components/empower.apps.managers.flowmanager.flowmanager']
# call(curl_terminal_command)

time.sleep(30)

curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/wilabt/flow7.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)