#! /bin/bash

export AUTOSSH_GATETIME=0
PORT=$(( (0x`tr "[:upper:]" "[:lower:]" <<< $HOSTNAME | md5sum | cut -c -8` % 61991) + 2000 )) # 2000 min port, 61991 random prime
echo "Forwarding on server port $PORT"
screen -dmS autossh-glcoud autossh greg@104.154.52.255 -R $PORT:localhost:22
screen -dmS autossh-stanford autossh greg@pion.stanford.edu -R $PORT:localhost:22
