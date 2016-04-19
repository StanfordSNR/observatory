#! /bin/bash
cd ~ && sudo apt-get install -y vim git screen autossh wicd-curses && git clone https://github.com:StanfordLPNG/diagnostic_box_scripts && sudo patch /etc/rc.local ~/diagnostic_box_scripts/field/rc.local-patch

#TODO:
#make username lpng
#raspi-config -- expand disk space
#change password
