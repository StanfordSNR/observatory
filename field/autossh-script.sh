#! /bin/bash

export AUTOSSH_GATETIME=0

screen -dmSL autossh-gcloud autossh lpng@104.196.19.245 -R 0:localhost:22
screen -dmSL autossh-aws autossh lpng@52.9.177.212 -R 0:localhost:22
