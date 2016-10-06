#! /bin/bash -x
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

touch /tmp/dont_reboot_automatically
mount -o remount,rw /
