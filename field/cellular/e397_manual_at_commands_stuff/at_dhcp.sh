echo -e AT^DHCP? > /dev/ttyUSB0
head -n 5 /dev/ttyUSB0 | tee temp_at_dhcp
