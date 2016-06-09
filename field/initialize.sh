#! /bin/bash

# raspi-config -- expand disk space

sudo su -c 'echo blacklist brcmfmac > /etc/modprobe.d/wlan-blacklist.conf'

echo "installing git screen autossh"
sudo apt-get update
sudo apt-get install -y vim git screen autossh

# Set up my dotfiles, also changes keyboard layout to US
echo "setting up greg dotfiles"
cd ~
git clone https://github.com/greghill/DotFiles.git
cd DotFiles
./initialize.sh

# Set up my diagnostic box scripts
echo "getting diagnostic box scripts"
cd ~
git clone https://github.com/StanfordLPNG/diagnostic_box_scripts

cd diagnostic_box_scripts/field

echo "changing timezone to Los Angeles"
sudo ./change_timezone.sh

echo "Adding cron jobs"
crontab cron_jobs

echo "Download cellular connectivity software? y/n (no if using wired etherenet only)"
#from http://tecadmin.net/bash-script-prompt-to-confirm-yes-no/#
while : ; do
        read -r -p -t 90000 "Are You Sure? [Y/n] " input

        case $input in
            [yY][eE][sS]|[yY])
                echo "Yes"
                sudo ./initialize_cellular_extras.sh
                ;;
        
            [nN][oO]|[nN])
                echo "No"
                ;;
        
            *)
                echo "Invalid input..."
                ;;
    esac
done

echo "Changing filesystem to be read-only on future boots"
sudo ./make_readonly_filesystem.sh

# Change password from raspberry, requires user input
passwd pi
# Change hostname from raspberrypi, requires user input
sudo ./change_hostname.sh

# make default ssh key and add to repo
cat /dev/zero | ssh-keygen -q -N ""
cat ~/.ssh/id_rsa.pub >> authorized_keys
git add authorized_keys
git commit -m "adding keys for $(cat /etc/hostname)"
git push
cd ../cloud
cp authorized_keys ~/.ssh/authorized_keys
cp known_hosts ~/.ssh/known_hosts

echo "will reboot on enter into readonly filesystem"
read
sudo reboot
