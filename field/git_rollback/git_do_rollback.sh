#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

sleep 15m
cd /home/pi/diagnostic_box_scripts/field
./mount_readwrite.sh
git reset --hard HEAD@{1}
crontab initialization/root_cron_jobs
/sbin/shutdown -r +2
