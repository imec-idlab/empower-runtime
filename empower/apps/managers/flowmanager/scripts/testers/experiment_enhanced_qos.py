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
parser.add_option("", "--sta1_ip", type="string", default="143.129.76.41")  # STA1 (sandbox)
parser.add_option("", "--sta2_ip", type="string", default="143.129.76.42")  # STA2 (sandbox)
parser.add_option("", "--sta3_ip", type="string", default="143.129.76.43")  # STA3 (sandbox)
parser.add_option("", "--tenant_id", type="string", default="8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719")  # sandbox
parser.add_option("", "--user", type="string", default="root")  # e.g., root, user
parser.add_option("", "--password", type="string", default="root")  # e.g., root, password
parser.add_option("", "--sta_user", type="string", default="root")  # e.g., root, user
parser.add_option("", "--sta_password", type="string", default="root")  # e.g., root, password
parser.add_option("", "--ssh_port", type="int", default=22)  # e.g., 22

(options, args) = parser.parse_args()


def create_ssh_client(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


print("Copying MGEN scipts into RPIs..")
# Copy MGEN script into RPI 1
ssh = create_ssh_client(str(options.sta1_ip), options.ssh_port, str(options.sta_user), str(options.sta_password))
scp = SCPClient(ssh.get_transport())
scp.put('mgen/sandbox/enhanced_qos/flow1.mgn', recursive=True, remote_path='/home/pi/mgen_scripts/')
scp.close()
ssh.close()
print("STA1 - Done!")

# Copy MGEN script into RPI 2
ssh = create_ssh_client(str(options.sta2_ip), options.ssh_port, str(options.sta_user), str(options.sta_password))
scp = SCPClient(ssh.get_transport())
scp.put('mgen/sandbox/enhanced_qos/flow2.mgn', recursive=True, remote_path='/home/pi/mgen_scripts/')
scp.close()
ssh.close()
print("STA2 - Done!")

# Copy MGEN script into RPI 3
ssh = create_ssh_client(str(options.sta3_ip), options.ssh_port, str(options.sta_user), str(options.sta_password))
scp = SCPClient(ssh.get_transport())
scp.put('mgen/sandbox/enhanced_qos/flow3.mgn', recursive=True, remote_path='/home/pi/mgen_scripts/')
scp.close()
ssh.close()
print("STA3 - Done!")

print("Advertising Flow 1...")
# Advertise flow 1
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/flow1.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Executing MGEN on RPI 1...")
# Execute MGEN script on RPI 1
ssh = create_ssh_client(str(options.sta1_ip), options.ssh_port, str(options.sta_user), str(options.sta_password))
# command = "ls \n ls -la"
command = "sudo killall mgen \n mgen input mgen_scripts/flow1.mgn > /dev/null 2>&1 &"
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command(command)
ssh.close()
print("Done!")

print("Sleeping...")
time.sleep(30)

print("Advertising Flow 2...")
# Advertise flow 2
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/flow2.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Executing MGEN on RPI 2...")
# Execute MGEN script on RPI 2
ssh = create_ssh_client(str(options.sta2_ip), options.ssh_port, str(options.sta_user), str(options.sta_password))
# command = "ls \n ls -la"
command = "sudo killall mgen \n mgen input mgen_scripts/flow2.mgn > /dev/null 2>&1 &"
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command(command)
ssh.close()
print("Done!")

print("Sleeping...")
time.sleep(30)

print("Advertising Flow 3...")
# Advertise flow 3
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/flow3.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")

print("Executing MGEN on RPI 3...")
# Execute MGEN script on RPI 3
ssh = create_ssh_client(str(options.sta3_ip), options.ssh_port, str(options.sta_user), str(options.sta_password))
# command = "ls \n ls -la"
command = "sudo killall mgen \n mgen input mgen_scripts/flow3.mgn > /dev/null 2>&1 &"
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command(command)
ssh.close()
print("Done!")

print("Sleeping...")
time.sleep(30)

print("Advertising and running Flow 4...")
# Advertise flow 3
# Curl terminal command for latency measurements
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/flow4.json',
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
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/flow5.json',
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
curl_terminal_command = ['curl', '-X', 'PUT', '-d', '@descriptors/sandbox/enhanced_qos/flow6.json',
                         'http://' + str(options.user) + ':' + str(options.password) + '@' +
                         str(options.controller_ip) + ':8888/api/v1/tenants/' + str(options.tenant_id) +
                         '/components/empower.apps.managers.flowmanager.flowmanager']
call(curl_terminal_command)
print("Done!")