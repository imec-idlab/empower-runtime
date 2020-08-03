#!/usr/bin/env bash

TENANT_ID=8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719
MINIMUM_QUANTUM=10
MAXIMUM_QUANTUM=12000
QUANTUM_DECREASE_RATE=0.7
QUANTUM_INCREASE_RATE=0.1
DB_MONITOR=True

# MCDA manager filename,
# the file must be placed in empower/apps/sandbox/managers/mcdamanager/descriptors/
# RSSI, Channel load, AP load, AP expected load, and Queue delay with different weights (QoS and BE)
MCDA_DESCRIPTOR="mcdainput.json"

# Running the APPs...
# MAC manager APP
#./empower-runtime.py apps.managers.macmanager --tenant_id=$TENANT_ID

# Slice manager APP
#./empower-runtime.py apps.managers.slicemanager --tenant_id=$TENANT_ID

# Hello World APP example
#./empower-runtime.py apps.helloworld.helloworld --tenant_id=$TENANT_ID

# Fixing STA positions (handover manager)
#./empower-runtime.py apps.sandbox.managers.handovermanager.handovermanager --tenant_id=$TENANT_ID

# Bin stats
#./empower-runtime.py apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# LVAP stats
#./empower-runtime.py apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# NCQM stats
#./empower-runtime.py apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# UCQM stats
#./empower-runtime.py apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Slice stats
#./empower-runtime.py apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# WiFi stats
#./empower-runtime.py apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Stats only
#./empower-runtime.py apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Stats + Managers
./empower-runtime.py apps.managers.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager --tenant_id=$TENANT_ID apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# WiFi Slicing
#./empower-runtime.py apps.sandbox.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager --tenant_id=$TENANT_ID apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.sandbox.managers.adaptiveslicemanager.adaptiveslicemanager --tenant_id=$TENANT_ID --minimum_quantum=$MINIMUM_QUANTUM --maximum_quantum=$MAXIMUM_QUANTUM --quantum_decrease_rate=$QUANTUM_DECREASE_RATE --quantum_increase_rate=$QUANTUM_INCREASE_RATE --db_monitor=$DB_MONITOR apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# No WiFi Slicing
#./empower-runtime.py apps.sandbox.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager --tenant_id=$TENANT_ID apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.sandbox.managers.mcdahandovermanager.mcdahandovermanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=$DB_MONITOR apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Sandbox APPs
#./empower-runtime.py apps.sandbox.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager --tenant_id=$TENANT_ID apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.sandbox.managers.adaptiveslicemanager.adaptiveslicemanager --tenant_id=$TENANT_ID --minimum_quantum=$MINIMUM_QUANTUM --maximum_quantum=$MAXIMUM_QUANTUM --quantum_decrease_rate=$QUANTUM_DECREASE_RATE --quantum_increase_rate=$QUANTUM_INCREASE_RATE --db_monitor=$DB_MONITOR apps.sandbox.managers.mcdahandovermanager.mcdahandovermanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=$DB_MONITOR apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Gomez User-Association
#./empower-runtime.py apps.sandbox.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager --tenant_id=$TENANT_ID apps.sandbox.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.sandbox.managers.gomezhandovermanager.gomezhandovermanager --tenant_id=$TENANT_ID apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

