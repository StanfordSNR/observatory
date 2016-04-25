echo -e AT^DHCP? > /dev/ttyUSB0
cat /dev/ttyUSB0 | tee temp_at_dhcp
