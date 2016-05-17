#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

cd /home/pi/diagnostic_box_scripts/field
apt-get install -y usb-modeswitch wvdial
# overwrite ethernet only cron jobs
crontab cron_jobs_cellular
