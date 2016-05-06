#! /bin/bash

export AUTOSSH_GATETIME=0

LOG_LOC_PREFIX="/home/pi/logfiles/screen/`date --iso-8601=minutes`"
screen -dmSL autossh-gcloud "script '$LOG_LOC_PREFIX'_gcloud; autossh lpng@104.196.19.245 -R 0:localhost:22"
screen -dmSL autossh-aws "'$LOG_LOC_PREFIX'_aws; autossh lpng@52.9.177.212 -R 0:localhost:22"
