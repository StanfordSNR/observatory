#! /bin/bash
GCLOUD_ADDRESS=lpng@23.251.141.221

export AUTOSSH_GATETIME=0;
export AUTOSSH_POLL=60; # poll for a connection every 60 seconds
while : ; do
    autossh $GCLOUD_ADDRESS -R 0:localhost:22 sleep
    sleep 5
    echo "autossh returned, restarting"
done
