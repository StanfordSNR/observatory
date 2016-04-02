#! /bin/bash

export AUTOSSH_GATETIME=0
PORT=`./hostname-to-port.sh $HOSTNAME`
echo "Forwarding on server port $PORT"
autossh greg@104.154.52.255 -R $PORT:localhost:22
