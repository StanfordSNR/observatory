RESPONSE=`cat temp_at_dhcp | grep DHCP: | cut -d: -f 2`
UNPACKED_RESPONSE=`perl -e 'print join(",",map { join(".", unpack("C4", pack("L", hex))) } split /,/, shift),"\n"' $RESPONSE`
IP=`echo $UNPACKED_RESPONSE | cut -d, -f 1`
MASK=`echo $UNPACKED_RESPONSE | cut -d, -f 2`
VIA=`echo $UNPACKED_RESPONSE | cut -d, -f 3`
echo "got $UNPACKED_RESPONSE"
sudo ifconfig wwan0 $IP netmask $MASK
sudo ip route add default via $VIA
echo nameserver 8.8.8.8 | sudo resolvconf -a wwan0
