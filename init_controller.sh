#!/usr/bin/env bash

# Sandbox tenant
TENANT_ID=8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719

# Adaptive Slicing Manager params
MINIMUM_QUANTUM=1
MAXIMUM_QUANTUM=12000
QUANTUM_DECREASE_RATE=0.1   # 90% decrease
QUANTUM_INCREASE_RATE=1.1   # 10% increase

# Adaptive STA Manager params
MINIMUM_BW=1
MAXIMUM_BW=100
BW_DECREASE_RATE=0.1   # 90% decrease
BW_INCREASE_RATE=1.1   # 10% increase

# General monitoring param
DB_MONITOR=True

# MCDA manager filename,
# the file must be placed in empower/apps/managers/mcdamanager/descriptors/
# RSSI, Channel load, AP load, AP expected load, and Queue delay with different weights (QoS and BE)
MCDA_DESCRIPTOR="mcdainput.json"

# Running the APPs...
# MAC manager APP
#./empower-runtime.py apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID

# Slice manager APP
#./empower-runtime.py apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID

# Fixing STA positions (handover manager)
#./empower-runtime.py apps.managers.handovermanager.statichandovermanager --tenant_id=$TENANT_ID

# Bin stats
#./empower-runtime.py apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# LVAP stats
#./empower-runtime.py apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# UPlink LVAP stats
#./empower-runtime.py empower.apps.handlers.uplinkstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

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
./empower-runtime.py apps.managers.handovermanager.handovermanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Traffic Shaping + Managers (Experiment 1 - scenarios A and B)
#./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.managers.adaptivelvapmanager.adaptivelvapmanager --tenant_id=$TENANT_ID --minimum_bw=$MINIMUM_BW --maximum_bw=$MAXIMUM_BW --bw_decrease_rate=$BW_DECREASE_RATE --bw_increase_rate=$BW_INCREASE_RATE --db_monitor=$DB_MONITOR

# Network Slicing + Managers (Experiment 1 - scenarios C and D)
#./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.managers.adaptiveslicemanager.adaptiveslicemanager --tenant_id=$TENANT_ID --minimum_quantum=$MINIMUM_QUANTUM --maximum_quantum=$MAXIMUM_QUANTUM --quantum_decrease_rate=$QUANTUM_DECREASE_RATE --quantum_increase_rate=$QUANTUM_INCREASE_RATE --db_monitor=$DB_MONITOR

# Delay-aware MCDA (Experiment 2 - all algorithms)
#./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.managers.adaptiveslicemanager.adaptiveslicemanager --tenant_id=$TENANT_ID --minimum_quantum=$MINIMUM_QUANTUM --maximum_quantum=$MAXIMUM_QUANTUM --quantum_decrease_rate=$QUANTUM_DECREASE_RATE --quantum_increase_rate=$QUANTUM_INCREASE_RATE --db_monitor=$DB_MONITOR apps.managers.mcdahandovermanager.mcdahandovermanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=$DB_MONITOR apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.managers.adaptivelvapmanager.adaptivelvapmanager --tenant_id=$TENANT_ID --minimum_bw=$MINIMUM_BW --maximum_bw=$MAXIMUM_BW --bw_decrease_rate=$BW_DECREASE_RATE --bw_increase_rate=$BW_INCREASE_RATE --db_monitor=$DB_MONITOR

# Delay-aware MCDA (Experiment 3 - user association algorithm only)
#./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.managers.mcdahandovermanager.mcdahandovermanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=$DB_MONITOR apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Delay-aware MCDA + slicing APPs (Experiment IM 2020)
#./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.managers.adaptiveslicemanager.adaptiveslicemanager --tenant_id=$TENANT_ID --minimum_quantum=$MINIMUM_QUANTUM --maximum_quantum=$MAXIMUM_QUANTUM --quantum_decrease_rate=$QUANTUM_DECREASE_RATE --quantum_increase_rate=$QUANTUM_INCREASE_RATE --db_monitor=$DB_MONITOR apps.managers.mcdahandovermanager.mcdahandovermanager --tenant_id=$TENANT_ID --descriptor=$MCDA_DESCRIPTOR --db_monitor=$DB_MONITOR apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

# Experiment Gomez (IM 2020 and current)
#./empower-runtime.py apps.managers.txpolicymanager.txpolicymanager --tenant_id=$TENANT_ID apps.managers.lvapmanager.lvapmanager --tenant_id=$TENANT_ID apps.managers.slicemanager.slicemanager --tenant_id=$TENANT_ID apps.managers.macmanager.macmanager --tenant_id=$TENANT_ID apps.managers.flowmanager.flowmanager --tenant_id=$TENANT_ID apps.managers.gomezhandovermanager.gomezhandovermanager --tenant_id=$TENANT_ID apps.handlers.lvapstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.wifistatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR apps.handlers.binstatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR  apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=$DB_MONITOR

