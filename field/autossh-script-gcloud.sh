#! /bin/bash

export AUTOSSH_GATETIME=0;
cd /tmp/logs/gcloud/screen
screen -dmSL autossh-gcloud autossh lpng@104.196.19.245 -R 0:localhost:22

OLD_PORT=0
while : ; do
    PORT=$(tac screenlog.* | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' '  -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        echo $PORT > gcloud.port
        scp gcloud.port lpng@104.196.19.245:diagnostic_box_scripts/cloud/dynamic_ports/$(hostname)
    fi
    OLD_PORT=$PORT
    sleep 2
done
