#! /bin/bash

export AUTOSSH_GATETIME=0;
cd /tmp/aws_logs/screen
CLOUD_ADDRESS=lpng@52.192.246.2
screen -dmSL autossh-aws autossh $CLOUD_ADDRESS -R 0:localhost:22 sleep

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
