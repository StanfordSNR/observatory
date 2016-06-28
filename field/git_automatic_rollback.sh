#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

sleep 4m
cd ~/diagnostic_box_scripts/field
./mount_readwrite.sh
git reset --hard master@{"30 minutes ago"}
crontab root_cron_jobs
shutdown -r +1
