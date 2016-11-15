#! /bin/bash -x

sudo apt-get update
sudo apt-get -y dist-upgrade
sudo apt-get install -y traceroute mosh dnsutils python-dev python-pip ntp ntpdate awscli
sudo pip install requests
sudo pip install matplotlib
