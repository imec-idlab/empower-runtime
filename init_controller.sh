#!/usr/bin/env bash

TENANT_ID=8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719
USER="user"
PASS="pass"

MINIMUM_QUANTUM=5
QUANTUM_DECREASE_RATE=0.3
QUANTUM_INCREASE_RATE=0.1

# Flow descriptor filename,
# the file must be placed in empower/apps/sandbox/managers/flowmanager/descriptors/
FLOW_DESCRIPTOR="experiment_run.json"       # 5 flows following POISSON distribution
#FLOW_DESCRIPTOR="single_flow.json"         # 1 flow of 5Mbps following PERIODIC distribution (testing purposes)
#FLOW_DESCRIPTOR="two_flows.json"           # 2 flows of 8Mbps following PERIODIC distribution (testing purposes)

# MCDA manager filename,
# the file must be placed in empower/apps/sandbox/managers/mcdamanager/descriptors/
MCDA_DESCRIPTOR="mcdainput.json"  # RSSI, Channel load, AP load, AP expected load, and Queue delay with different weights
#MCDA_DESCRIPTOR="ref_equal.json"  # RSSI, Channel load, and AP load with equal weights

# Running the APPs...
# MAC manager APP
#./empower-runtime.py apps.macmanager.macmanager --tenant_id=e536c433-d843-45e7-9b89-56bf50f7b928

# Hello World APP example
# ./empower-runtime.py apps.helloworld.helloworld --tenant_id=49fef5d5-f306-4af8-99a9-ef106538a983

# Fixing STA positions (handover manager)
# ./empower-runtime.py apps.sandbox.managers.handovermanager.handovermanager --tenant_id=$TENANT_ID

# Slice stats only
# ./empower-runtime.py apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS

# Slice stas + flow manager
# ./empower-runtime.py apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID --descriptor=$FLOW_DESCRIPTOR

# No WiFi Slice Manager
# ./empower-runtime.py apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID --descriptor=$FLOW_DESCRIPTOR apps.sandbox.managers.mcdamanager.mcdamanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=True --db_user=$USER --db_pass=$PASS --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.binstatshandler --db_monitor=True --db_user=$USER --db_pass=$PASS --tenant_id=$TENANT_ID apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS

# Sandbox APPs
./empower-runtime.py apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID --descriptor=$FLOW_DESCRIPTOR apps.sandbox.managers.wifislicemanager.wifislicemanager --tenant_id=$TENANT_ID --minimum_quantum=$MINIMUM_QUANTUM --quantum_decrease_rate=$QUANTUM_DECREASE_RATE --quantum_increase_rate=$QUANTUM_INCREASE_RATE apps.sandbox.managers.mcdamanager.mcdamanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=True --db_user=$USER --db_pass=$PASS --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.binstatshandler --db_monitor=True --db_user=$USER --db_pass=$PASS --tenant_id=$TENANT_ID apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS

