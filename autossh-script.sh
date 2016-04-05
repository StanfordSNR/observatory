#! /bin/bash

export AUTOSSH_GATETIME=0
screen -dmS autossh-glcoud autossh lpng@104.196.19.245 -R 58100:localhost:22
screen -dmS autossh-stanford autossh lpng@pion.stanford.edu -R 58104:localhost:22
