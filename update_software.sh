#! /bin/bash -x

sudo apt-get update
sudo apt-get -y dist-upgrade
sudo apt-get install -y usb-modeswitch wvdial traceroute mosh dnsutils python-pip
sudo pip install requests
