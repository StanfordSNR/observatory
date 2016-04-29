while : ; do
    echo sleep 5s
    sleep 5s
    echo ./generic_huawei_modeswitch
    ./generic_huawei_modeswitch
    echo sleep 5s
    sleep 5s
    echo sudo wvdial E397
    sudo wvdial E397
    echo sudo wvdial E531
    sudo wvdial E3531
done
