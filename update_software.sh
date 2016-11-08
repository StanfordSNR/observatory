#! /bin/bash -x

sudo apt-get update
sudo apt-get -y dist-upgrade
sudo apt-get install -y usb-modeswitch wvdial traceroute mosh dnsutils python-dev python-pip
sudo pip install requests
sudo pip install matplotlib
