#! /bin/bash
CONTENTS=$(
date --iso-8601=minutes
)
echo $CONTENTS
COMMAND="echo $CONTENTS >> diagnostic_box_scripts/cloud/status_logs/$(hostname)"
ssh lpng@52.9.177.212 $COMMAND &
ssh lpng@104.196.19.245 $COMMAND
