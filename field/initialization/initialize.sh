#! /bin/bash -x

echo "updating and installing extra utilities"
sudo apt-get update
sudo apt-get -y dist-upgrade
sudo apt-get install -y vim git autossh dialog w3m dnsutils traceroute ntp resolvconf dig python3

# Set up my dotfiles, also changes keyboard layout to US
echo "setting up greg dotfiles"
cd ~
git clone https://github.com/greghill/DotFiles.git && cd DotFiles && ./initialize.sh

echo "getting robust remote connect"
cd ~
git clone https://github.com/StanfordLPNG/robust_remote_connect

echo "getting diagnostic box scripts"
cd ~
git clone https://github.com/StanfordLPNG/diagnostic_box_scripts

cd ~/diagnostic_box_scripts/field/initialization

dialog --yesno 'Download cellular connectivity software? (no if using wired etherenet only)' 5 80
# from https://bash.cyberciti.biz/guide/A_yes/no_dialog_box
response=$?
case $response in
    0) ./initialize_cellular_extras.sh;;
    1) echo "Not installed.";;
    255) echo "[ESC] key pressed. Extras not installed";;
esac

dialog --yesno 'Is this a raspberry pi?' 5 80
response=$?
case $response in
    0) ./initialize_rpi_specific.sh;;
    1) echo "Extras not installed.";;
    255) echo "[ESC] key pressed. Extras not installed";;
esac

# make default ssh key that is command restricted and add to repo
if [ ! -f ~/.ssh/id_rsa ]
then
    mkdir -p ~/.ssh
    ssh-keygen -q -N "" -f ~/.ssh/id_rsa < /dev/zero
    RESTRICTED_KEY="command=\"~/diagnostic_box_scripts/cloud/cloud_util.py $(cat /etc/hostname) \$SSH_ORIGINAL_COMMAND\", $(cat ~/.ssh/id_rsa.pub)"
    git pull --ff-only # make sure we aren't behind already
    echo $RESTRICTED_KEY >> authorized_keys
    git add authorized_keys
    git commit -m "adding command restricted key for $(cat /etc/hostname) for cloud servers to add to authorized_keys"
    git push
fi

cd ~/diagnostic_box_scripts/cloud
cp authorized_keys ~/.ssh/authorized_keys
cp known_hosts ~/.ssh/known_hosts

echo "Adding cron jobs"
cd ~/diagnostic_box_scripts/field/initialization
crontab user_cron_jobs
sudo crontab root_cron_jobs

echo "will reboot on enter"
read -t 90001
sudo reboot
