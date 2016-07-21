#!/bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

cd /home/pi/diagnostic_box_scripts/field
./mount_readwrite.sh
pkill git_do_rollback
crontab initialization/root_cron_jobs # necessary to not reboot with git_rollback script
