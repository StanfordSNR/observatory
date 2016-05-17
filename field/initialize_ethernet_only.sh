#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

#raspi-config -- expand disk space

#ssh-known hosts and authorized_keys

echo "installing git screen autossh"
sudo apt-get install -y vim git screen autossh

# Set up my dotfiles, also changes keyboard layout to US
echo "setting up greg dotfiles"
cd /home/pi
git clone https://github.com/greghill/DotFiles.git && cd DotFiles && sudo ./initialize.sh

# Set up my diagnostic box scripts
echo "setting up cron jobs, making filesytem readonly on reboot"
cd /home/pi
git clone https://github.com/StanfordLPNG/diagnostic_box_scripts

cd diagnostic_box_scripts/field
crontab cron_jobs_ethernet_only

sudo ./make_readonly_filesystem.sh

echo "changing timezone to Los Angeles"
sudo timezone/change_timezone.sh

# Change password from raspberry, requires user input
passwd pi
# Change hostname from raspberrypi, requires user input
sudo ./change_hostname.sh
echo "will reboot on enter to establish changed hostname"
read
sudo reboot
