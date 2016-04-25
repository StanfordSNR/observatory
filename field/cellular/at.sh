echo -e AT > /dev/ttyUSB0
cat /dev/ttyUSB0 | tee temp_at_nop
