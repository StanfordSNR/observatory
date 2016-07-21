#!/bin/bash -xe
exit 1
sudo /home/pi/diagnostic_box_scripts/field/mount_readwrite.sh
git pull --ff-only
crontab /home/pi/diagnostic_box_scripts/field/initialization/user_cron_jobs
sudo crontab -l > /tmp/newcrontab
cat /home/pi/diagnostic_box_scripts/field/git_rollback/root_git_rollback_cron_job >> /tmp/newcrontab
sudo crontab /tmp/newcrontab
sudo reboot
