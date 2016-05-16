echo -e "AT\r" > /dev/ttyUSB0
head -n 10 /dev/ttyUSB0 | tee temp_at_nop
