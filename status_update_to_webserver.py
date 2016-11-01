#! /usr/bin/python3
import argparse
from datetime import datetime
import requests

parser = argparse.ArgumentParser(description='Perform status update POST on behalf of a field box.')

parser.add_argument('hostname', type=str, help='hostname of field box')

parser.add_argument('--git-head', help='SHA-1 hash of git head for diagnostic_box_scripts repository on field box')

parser.add_argument('--temp', help='Temperature of field box in degress Celsius.')

parser.add_argument('--uptime', nargs='+', help='report the results of running the command: uptime')

parser.add_argument('--public-ip', help='Public IP of field box')

args = parser.parse_args()

cur_time = datetime.utcnow()
cur_time = cur_time.replace(microsecond=0)
payload = {'hostname': args.hostname, 'datetime': cur_time.isoformat()}

if args.git_head is not None:
    payload['head'] = args.git_head

if args.temp is not None:
    payload['temp'] = args.temp
else:
    payload['temp'] = str(0.0)

if args.public_ip is not None:
    payload['public_ip'] = args.public_ip

# Uptime needs to go last as it is a multiple word output
if args.uptime is not None:
    payload['uptime'] = ' '.join(args.uptime)

r = requests.post("https://network-observatory.herokuapp.com/post-measurement-box-checkin", data=payload)

print("POST returned " + str(r.status_code) +": " + r.text)
