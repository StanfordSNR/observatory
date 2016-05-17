#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

LANG=en_US.UTF_8 locale-gen --purge en_US.UTF_8
dpkg-reconfigure -f noninteractive locales
