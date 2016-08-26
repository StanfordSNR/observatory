#! /bin/bash -x

sudo apt-get install -y vim usb-modeswitch wvdial
sudo ln -s /etc/ppp/pap-secrets /tmp/.ppp.pap-secrets
sudo ln -s /etc/ppp/chap-secrets /tmp/.ppp.chap-secrets
