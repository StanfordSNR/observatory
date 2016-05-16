#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

#raspi-config -- expand disk space

#change password

#ssh-known hosts and authorized_keys

#change hostname

sudo apt-get install -y vim git screen autossh
cd ~

# Set up my dotfiles
mv .bashrc .bashrc.old
git clone https://github.com/greghill/DotFiles.git && ln DotFiles/.* .

# Set up my diagnostic box scripts
git clone https://github.com/StanfordLPNG/diagnostic_box_scripts
cd diagnostic_box_scripts/field

crontab cron_jobs_ethernet_only

# Change password from raspberry, requires user input
passwd pi
# Change hostname from raspberrypi, requires user input
sudo ./change_hostname.sh
echo "will reboot on enter to establish changed hostname"
read
sudo reboot
