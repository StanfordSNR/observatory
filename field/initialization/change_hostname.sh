#! /bin/bash -x
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

echo "enter new hostname"
read -t 90000 NEW_HOSTNAME
if [ $(echo -n $NEW_HOSTNAME | wc -w) -eq 1 ] && [ $(echo -n $NEW_HOSTNAME | wc -m) -gt 0 ] # check new hostname exactly one word with positive length
then
    sed "s/\(127\.0\.1\.1[[:space:]]*\)[[:alnum:]]*/\1$NEW_HOSTNAME/g" /etc/hosts > /tmp/hosts
    mv /tmp/hosts /etc/hosts
    echo "$NEW_HOSTNAME" > /etc/hostname
    hostname $NEW_HOSTNAME # think this is temp until restart which is fine because above will change for after restart
else
    echo invalid hostname: $NEW_HOSTNAME
fi
