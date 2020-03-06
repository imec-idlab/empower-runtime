#!/usr/bin/env bash

TENANT_ID=8aaca1c6-bf3c-4455-8c6d-4e4b6eef7719
USER="user"
PASS="pass"

# MAC manager
#./empower-runtime.py apps.macmanager.macmanager --tenant_id=e536c433-d843-45e7-9b89-56bf50f7b928

# Hello World example
# ./empower-runtime.py apps.helloworld.helloworld --tenant_id=49fef5d5-f306-4af8-99a9-ef106538a983

# Sandbox APPs
./empower-runtime.py apps.sandbox.managers.handovermanager --tenant_id=$TENANT_ID apps.handlers.ncqmstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.ucqmstatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS apps.handlers.binstatshandler --db_monitor=True --db_user=$USER --db_pass=$PASS --tenant_id=$TENANT_ID apps.handlers.slicestatshandler --tenant_id=$TENANT_ID --db_monitor=True --db_user=$USER --db_pass=$PASS

