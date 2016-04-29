RESPONSE=`cat temp_at_dhcp | grep DHCP: | head | cut -d: -f 2`
UNPACKED_RESPONSE=`perl -e 'print join(", ",map { join(".", unpack("C4", pack("L", hex))) } split /,/, shift),"\n"' $RESPONSE`
IP=`echo $UNPACKED_RESPONSE | cut -d, -f 1`
MASK=`echo $UNPACKED_RESPONSE | cut -d, -f 2`
VIA=`echo $UNPACKED_RESPONSE | cut -d, -f 3`
DNS1=`echo $UNPACKED_RESPONSE | cut -d, -f 5`
DNS2=`echo $UNPACKED_RESPONSE | cut -d, -f 6`

echo "got $UNPACKED_RESPONSE"

IFACE_CMD="sudo ifconfig wwan0 $IP netmask $MASK"
echo $IFACE_CMD
$IFACE_CMD

ROUTE_CMD="sudo ip route add default via $VIA"
echo $ROUTE_CMD
$ROUTE_CMD

DNS_ENTRIES="nameserver $DNS1\nnameserver $DNS2\n"
echo -e "adding \n$DNS_ENTRIES to resolvconf"
echo -e $DNS_ENTRIES | sudo resolvconf -a wwan0
