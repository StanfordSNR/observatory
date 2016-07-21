#! /bin/bash -e #abort if any command turns nonzero
sudo ./mount_readwrite.sh
git pull --ff-only
crontab /home/pi/diagnostic_box_scripts/field/initialization/user_cron_jobs
sudo crontab -l > /tmp/newcrontab
echo root_git_rollback_cron_job >> /tmp/newcrontab
sudo crontab /tmp/newcrontab
sudo reboot
