#!/bin/sh -x

sudo apt-get update
sudo apt-get -y dist-upgrade
sudo apt-get -yq --force-yes install traceroute mosh dnsutils python-dev \
             python-pip ntp ntpdate awscli python-matplotlib
sudo pip install requests
