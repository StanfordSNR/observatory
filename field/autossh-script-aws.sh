#! /bin/bash

export AUTOSSH_GATETIME=0;
mkdir /tmp/logs /tmp/logs/aws /tmp/logs/gcloud /tmp/logs/aws/autossh /tmp/logs/gcloud/autossh /tmp/logs/aws/screen /tmp/logs/gcloud/screen /tmp/logs/autoconnect
cd /tmp/logs/aws/screen
screen -dmSL autossh-aws autossh lpng@52.9.177.212 -R 0:localhost:22

OLD_PORT=0
while : ; do
    PORT=$(tac ~/screenlog.* | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' '  -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        echo $PORT > aws.port
        scp lpng@52.9.177.212:diagnostic_box_scripts/cloud/aws.port
    fi
    OLD_PORT=$PORT
    sleep 2
done
