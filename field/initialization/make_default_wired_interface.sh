#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

grep -q "eth0:0" /etc/network/interfaces
if [ $? = 0 ]
    then
        echo "eth0:0 interface probably already exists, exiting"
        exit 1
    fi

echo "
# always present static in case no dhcp
auto eth0:0
iface eth0:0 inet static
	address 192.168.10.10
	netmask 255.255.255.0" >> /etc/network/interfaces
