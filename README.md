autossh-script called by /etc/rc.local

For a local username greg we include in rc.local:

`sudo -u greg screen -dmS autossh-session /home/greg/diagnostic_box_scripts/autossh-script.sh`
