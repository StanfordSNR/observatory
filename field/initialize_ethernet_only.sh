#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

#raspi-config -- expand disk space

# apt update/upgrade?
# hotplug eth0?

#ssh-known hosts and authorized_keys

echo "installing git screen autossh"
sudo apt-get install -y vim git screen autossh

# Set up my dotfiles, also changes keyboard layout to US
echo "setting up greg dotfiles"
cd /home/pi
git clone https://github.com/greghill/DotFiles.git && cd DotFiles && sudo ./initialize.sh

# Set up my diagnostic box scripts
echo "getting diagnostic box scripts"
cd /home/pi
git clone https://github.com/StanfordLPNG/diagnostic_box_scripts

cd diagnostic_box_scripts/field

echo "changing timezone to Los Angeles, locale to US"
sudo change_timezone.sh
sudo change_locales.sh

echo "Adding cron jobs"
crontab cron_jobs_ethernet_only

# Change password from raspberry, requires user input
passwd pi
# Change hostname from raspberrypi, requires user input
sudo ./change_hostname.sh

sudo ./make_readonly_filesystem.sh
echo "will reboot on enter into readonly filesystem"
read
sudo reboot
