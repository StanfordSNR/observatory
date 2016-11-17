#! /bin/bash -x
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [wvdial_script]"
    exit 1
fi


while : ; do
    while ! lsusb | grep -i huawei;
    do
        echo "no huawei devices found"
        sleep 5s
    done


    # run modeswitch if Huawei device not in modem mode
    if ! lsusb | grep -i "1506 Huawei"; then
        sleep 10s
        /home/pi/observatory_box_scripts/cellular/generic_huawei_modeswitch.sh
    fi

    sleep 20s
    # run wvdial command supplied by user
    $1
done
