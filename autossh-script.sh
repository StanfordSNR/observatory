#! /bin/bash

GCLOUD_PORT=58100
PION_PORT=58104
AWS_PORT=58108
export AUTOSSH_GATETIME=0
screen -dmS autossh-glcoud autossh lpng@104.196.19.245 -R $GCLOUD_PORT:localhost:22
screen -dmS autossh-stanford autossh lpng@pion.stanford.edu -R $PION_PORT:localhost:22
screen -dmS autossh-aws autossh lpng@52.9.177.212 -R $AWS_PORT:localhost:22
