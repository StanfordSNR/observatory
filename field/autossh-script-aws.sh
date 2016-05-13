#! /bin/bash

export AUTOSSH_GATETIME=0;
cd /tmp/logs/aws/screen
screen -dmSL autossh-aws autossh lpng@52.9.177.212 -R 0:localhost:22

OLD_PORT=0
while : ; do
    PORT=$(tac screenlog.* | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' '  -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        echo $PORT > aws.port
        scp aws.port lpng@52.9.177.212:diagnostic_box_scripts/cloud/dynamic_ports/$(hostname)
    fi
    OLD_PORT=$PORT
    sleep 2
done
