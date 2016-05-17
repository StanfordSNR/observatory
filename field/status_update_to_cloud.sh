#! /bin/bash
CONTENTS=$(
date --iso-8601=minutes;
echo -ne "\ndiagnostic_box_scripts HEAD="
cd /home/pi/diagnostic_box_scripts && git rev-parse HEAD;
/opt/vc/bin/vcgencmd measure_temp | sed s/\'//g
)
echo $CONTENTS
COMMAND="echo $CONTENTS >> diagnostic_box_scripts/cloud/status_logs/$(hostname)"
ssh lpng@52.192.246.2 $COMMAND &
ssh lpng@23.251.141.221 $COMMAND
