while : ; do
    while ! lsusb | grep -i huawei;
    do
        echo "no huawei devices found"
        sleep 1s
    done
    echo sleep 5s
    sleep 5s
    echo generic_huawei_modeswitch.sh
    /home/pi/diagnostic_box_scripts/field/cellular/generic_huawei_modeswitch.sh
    echo sleep 5s
    sleep 5s
    echo sudo wvdial E397
    sudo wvdial E397
    echo sudo wvdial E531
    sudo wvdial E3531
    #temp hack for dhcp
    echo sudo dhclient eth1
    sudo dhclient eth1

    # if we fall to here make sure to restart autossh connections
    echo pkill autossh --signal USR1
    pkill autossh --signal USR1
one
