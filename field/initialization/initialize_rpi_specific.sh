# TODO test remove fake-hwclock
# sudo apt-get autoremove fake-hwclock
# sudo rm /etc/cron.hourly/fake-hwclock
# sudo rm /etc/fake-hwclock.data

cd ~/diagnostic_box_scripts/field/initialization
echo "changing timezone to Los Angeles"
sudo ./change_timezone.sh

echo "Changing filesystem to be read-only on future boots"
sudo ./make_readonly_filesystem.sh

# Change password from raspberry, requires user input
passwd pi

echo "disabling wifi/bluetooth/sound"
sudo cp raspi-blacklist.conf /etc/modprobe.d/

echo "Adding eth0:0 so can always ssh with local cable to 192.168.10.10"
sudo ./make_default_wired_interface.sh
