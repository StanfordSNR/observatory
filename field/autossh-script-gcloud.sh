#! /bin/bash

export AUTOSSH_GATETIME=0;
cd /tmp/gcloud_logs/screen
screen -dmSL autossh-gcloud autossh lpng@23.251.141.221 -R 0:localhost:22

OLD_PORT=0
while : ; do
    PORT=$(tac screenlog.* | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' '  -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        echo $PORT > gcloud.port
        scp gcloud.port lpng@23.251.141.221:diagnostic_box_scripts/cloud/dynamic_ports/$(hostname)
    fi
    OLD_PORT=$PORT
    sleep 1
done
