#! /bin/bash

export AUTOSSH_GATETIME=0

PORT=$(/home/lpng/diagnostic_box_scripts/field/machine_to_port.py $HOSTNAME)
screen -dmS autossh-gcloud autossh lpng@104.196.19.245 -R $PORT:localhost:22
screen -dmS autossh-aws autossh lpng@52.9.177.212 -R $PORT:localhost:22
