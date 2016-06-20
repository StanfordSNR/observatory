#! /bin/bash

cd /tmp/gcloud_logs/screen
CLOUD_ADDRESS=lpng@23.251.141.221
screen -dmSL autossh-gcloud ~/diagnostic_box_scripts/field/autossh-inner-loop.sh $CLOUD_ADDRESS

OLD_PORT=0
while : ; do
    PORT=$(tac screenlog.* | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' ' -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        ssh $CLOUD_ADDRESS "set_port --port $PORT"
    fi
    OLD_PORT=$PORT
    sleep 1
done
