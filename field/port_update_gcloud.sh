#! /bin/bash

cd /tmp/gcloud_logs
GCLOUD_ADDRESS=lpng@23.251.141.221

OLD_PORT=0
while : ; do
    PORT=$(tac autossh_gcloud.log | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' ' -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        ssh $GCLOUD_ADDRESS "set_port --port $PORT"
    fi
    OLD_PORT=$PORT
    sleep 1
done
