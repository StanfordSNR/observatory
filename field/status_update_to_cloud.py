#! /usr/bin/python3
import argparse
from subprocess import call, check_output
import ipaddress

parser = argparse.ArgumentParser(description='Get various statistics to send to cloud box')

parser.add_argument('cloud_username', type=str, help='username to SSH into for cloud box')

parser.add_argument('cloud_ip', type=ipaddress.ip_address, help='IP address of cloud box')

args = parser.parse_args()

status_update_command = ['ssh', args.cloud_username + '@' + str(args.cloud_ip), 'allowed-command --command /home/lpng/diagnostic_box_scripts/cloud/status_update_to_webserver.py']

hostname = check_output("hostname")
status_update_command += [hostname]

# command to get core temperature of Rasperry Pi
temp_results = check_output("/opt/vc/bin/vcgencmd measure_temp | sed s/[^0-9.]*//g", shell=True)
try:
    float(temp_results)
    status_update_command += ["--temp", temp_results]
except ValueError:
    # command probably didn't exist, don't include temp in status update
    pass

git_head_results = check_output("cd ~/diagnostic_box_scripts && git rev-parse HEAD", shell=True)
status_update_command += ["--git-head", git_head_results]

uptime_results = check_output("uptime")
status_update_command += ["--uptime", uptime_results]

public_ip = check_output("dig TXT +short o-o.myaddr.l.google.com @ns1.google.com | sed 's/\"//g'", shell=True)
status_update_command += ["--public-ip", public_ip]

call(status_update_command)
