#! /bin/bash
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

while : ; do
    while ! lsusb | grep -i huawei;
    do
        echo "no huawei devices found"
        sleep 1s
    done
    echo sleep 2s
    sleep 2s
    echo generic_huawei_modeswitch.sh
    /home/pi/diagnostic_box_scripts/field/cellular/generic_huawei_modeswitch.sh
    echo sleep 5s
    sleep 5s
    echo  wvdial E397
     wvdial E397
    echo  wvdial E531
     wvdial E3531
    #temp hack for dhcp
    echo  dhclient eth1
    dhclient eth1

    # if we fall to here make sure to restart autossh connections
    echo pkill autossh --signal USR1
    pkill autossh --signal USR1
done
