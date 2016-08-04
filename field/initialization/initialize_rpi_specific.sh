cd ~/diagnostic_box_scripts/field/initialization
echo "changing timezone to Los Angeles"
sudo ./change_timezone.sh

echo "Changing filesystem to be read-only on future boots"
sudo ./make_readonly_filesystem.sh

# Change password from raspberry, requires user input
passwd pi
# Change hostname, requires user input
sudo ./change_hostname.sh

echo "disabling wifi/bluetooth/sound"
sudo cp raspi-blacklist.conf /etc/modprobe.d/
