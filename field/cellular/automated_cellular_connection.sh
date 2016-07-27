#! /bin/bash -x
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

while : ; do
    while ! lsusb | grep -i huawei;
    do
        echo "no huawei devices found"
        sleep 5s
    done
    sleep 2s
    /home/pi/diagnostic_box_scripts/field/cellular/generic_huawei_modeswitch.sh
    sleep 5s
    wvdial att E397
    wvdial tmobile E397
    wvdial att E3531
    wvdial tmobile E3531

    # if we fall to here make sure to restart autossh connections
    pkill autossh --signal USR1
done
