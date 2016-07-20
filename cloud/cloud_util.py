#! /usr/bin/python3
import argparse
import time
from datetime import datetime
import os
import requests

parser = argparse.ArgumentParser(description='Handle status updates and reporting ssh remote forwarding dynamic ports for field boxes.')

parser.add_argument('hostname', type=str, help='hostname of field box')

parser.add_argument('command', type=str, choices=["set_port", "web_checkin", "sleep"], help='action to be taken')

parser.add_argument('--port', help='Port number on cloud machine ssh remote forwarded to a field box with the given hostname.')

parser.add_argument('--git_head', help='SHA-1 hash of git head for diagnostic_box_scripts repository on field box')

parser.add_argument('--temp', help='Temperature of field box in degress Celsius.')

parser.add_argument('--uptime', help='report the results of running the command: uptime')

args = parser.parse_args()

if args.command == "set_port":
    if args.port is None:
        print("Must use --port option to set port.")
    else:
        print("setting port")
        temp_port_filename = '/tmp/.' + args.hostname + str(time.perf_counter())
        f = open(temp_port_filename, 'w')
        f.write(args.port)
        f.flush()
        os.fsync(f.fileno())
        f.close()

        proper_port_filename = os.path.expanduser('~/diagnostic_box_scripts/cloud/dynamic_ports/' + args.hostname)
        os.rename(temp_port_filename, proper_port_filename)

if args.command == "web_checkin":
    cur_time = datetime.utcnow()
    cur_time = cur_time.replace(microsecond=0)
    payload = {'hostname': args.hostname, 'datetime': cur_time.isoformat()}

    if args.git_head is not None:
        payload['head'] = args.git_head
    if args.temp is not None:
        payload['temp'] = args.temp
    if args.uptime is not None:
        payload['uptime'] = args.uptime

    r = requests.post("https://network-observatory.herokuapp.com/post-measurement-box-checkin", data=payload)

    print("post returned: " + str(r.status_code))
    #print(r.text)

if args.command == "sleep":
    time_sleep = 4000 # 66 mins
    print("Sleeping " + str(time_sleep) + " seconds")
    time.sleep(time_sleep)
