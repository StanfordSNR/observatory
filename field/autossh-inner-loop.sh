#! /bin/bash
if [ "$#" -ne 1 ]; then
    echo "usage: $0 user@ip"
    exit 1
fi

export AUTOSSH_GATETIME=0;
export AUTOSSH_POLL=60; # poll for a connection every 60 seconds
while : ; do
    autossh $1 -R 0:localhost:22 sleep
    sleep 5
    echo "autossh returned, restarting"
done
