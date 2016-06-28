#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

echo "America/Los_Angeles" > /etc/timezone
dpkg-reconfigure -f noninteractive tzdata
