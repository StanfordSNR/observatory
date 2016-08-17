#! /usr/bin/python3
import argparse
from subprocess import call
import ipaddress

parser = argparse.ArgumentParser(description='Get various statistics to send to cloud box')

parser.add_argument('cloud_username', type=str, help='username to SSH into for cloud box')

parser.add_argument('cloud_ip', type=ipaddress.ip_address, help='IP address of cloud box')

args = parser.parse_args()

status_update_cmd = ["ssh", args.cloud_username + "@" + str(args.cloud_ip), "--allowed-command", "/home/lpng/cloud/status_update_to_webserver.py"]

# Only run if temp command exists
temp_results = call("/opt/vc/bin/vcgencmd measure_temp")
status_update_command += ["--temp", temp_results]

git_head_results = call("cd ~/diagnostic_box_scripts && git rev-parse HEAD", shell=True)
status_update_command += ["--git-head", git_head_results]

uptime_results = call("uptime")
status_update_command += ["--uptime", uptime_results]

call(status_update_command)
