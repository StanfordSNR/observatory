#! /bin/bash
cd ~/diagnostic_box_scripts #so we can get git head

# If temp script doesn't exist/work default to 0
TEMP=$(/opt/vc/bin/vcgencmd measure_temp)
if [ $? -eq 0 ]
    then
    TEMP=$(echo $TEMP | sed s/[^0-9.]*//g)
else
    TEMP=0
fi

COMMAND="web_checkin --git_head=$(git rev-parse HEAD) --temp=$TEMP"

ssh lpng@52.192.246.2 $COMMAND &
ssh lpng@23.251.141.221 $COMMAND
