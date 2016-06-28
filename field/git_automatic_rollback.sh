#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

sleep 10m
cd /home/pi/diagnostic_box_scripts/field
./mount_readwrite.sh
crontab root_cron_jobs
git reset --hard HEAD@{1}
shutdown -r +1
