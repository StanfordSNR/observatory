#! /bin/bash -x
AWS_ADDRESS=lpng@52.192.246.2

export AUTOSSH_GATETIME=0;
export AUTOSSH_POLL=60; # poll for a connection every 60 seconds
while : ; do
    autossh $AWS_ADDRESS -R 0:localhost:22 sleep
    sleep 5
    echo "autossh returned, restarting"
done
