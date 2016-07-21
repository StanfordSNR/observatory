#!/bin/bash -xe
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

# run after a git pull to setup cron jobs and rollback if not cancelled on reboot
crontab -u pi /home/pi/diagnostic_box_scripts/field/initialization/user_cron_jobs
grep -v '/sbin/shutdown' /home/pi/diagnostic_box_scripts/field/initialization/root_cron_jobs > /tmp/newcrontab # put crontab lines that aren't shutdown into temp file
cat /home/pi/diagnostic_box_scripts/field/git_rollback/root_git_rollback_cron_job >> /tmp/newcrontab # add git rollback lines
crontab /tmp/newcrontab
/sbin/shutdown -r now
