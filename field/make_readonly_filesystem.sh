#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

grep -q ",ro" /etc/fstab
if [ $? = 0 ]
    then
        echo "filesystem probably already read only, exiting"
        exit 1
    fi

echo "mount /tmp/ in ram"
systemctl enable tmp.mount

echo "add ro options to /etc/fstab"
sed -i -e '/\/dev\/mmcblk0/ s/defaults/defaults,ro/g' /etc/fstab
