#! /bin/bash
cd ~/diagnostic_box_scripts #so we can get git head
COMMAND="web_checkin --git_head=$(git rev-parse HEAD) --temp=$(/opt/vc/bin/vcgencmd measure_temp | sed s/[^0-9.]*//g)"

ssh lpng@52.192.246.2 $COMMAND &
ssh lpng@23.251.141.221 $COMMAND
