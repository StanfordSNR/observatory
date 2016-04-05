#! /bin/bash

GCLOUD_PORT=58100
PION_PORT=58104
export AUTOSSH_GATETIME=0
screen -dmS autossh-glcoud autossh lpng@104.196.19.245 -R $GCLOUD_PORT:localhost:22
screen -dmS autossh-stanford autossh lpng@pion.stanford.edu -R $PION_PORT:localhost:22
