#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

cp /home/pi/diagnostic_box_scripts/field/timezone/etc_timezone /etc/timezone
dpkg-reconfigure -f noninteractive tzdata
