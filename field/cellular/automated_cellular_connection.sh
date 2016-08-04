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
    sleep 5s
    /home/pi/diagnostic_box_scripts/field/cellular/generic_huawei_modeswitch.sh
    sleep 10s
    wvdial E3531 safaricom

    # if we fall to here make sure to restart autossh connections
    pkill autossh --signal USR1
done
