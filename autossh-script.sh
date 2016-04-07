#! /bin/bash

export AUTOSSH_GATETIME=0

# choose port between 2000, 65499 based on the first 64 bits of the md5sum of the case-insensitive hostname (63499 is a prime number)
PORT=$(( (0x`tr "[:upper:]" "[:lower:]" <<< $HOSTNAME | md5sum | cut -c -16` % 63499) + 2000 ))

screen -dmS autossh-glcoud autossh lpng@104.196.19.245 -R $PORT:localhost:22
screen -dmS autossh-aws autossh lpng@52.9.177.212 -R $PORT:localhost:22
