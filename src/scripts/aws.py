#!/usr/bin/env python

import sys
import argparse

import context
from helpers import utils
from helpers.subprocess_wrappers import Popen, check_output, PIPE


def main():
    config = utils.parse_vantage_points()

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    parser.add_argument('--hosts', metavar='"HOST1 HOST2..."',
                        help='space-separated list of hosts (default: all)')
    args = parser.parse_args()

    applied_hosts = None
    if args.hosts is not None:
        applied_hosts = args.hosts.split()

    procs = []
    for server, server_cfg in config['aws_servers'].iteritems():
        if applied_hosts is not None:
            if server not in applied_hosts:
                continue

        instance_id = server_cfg['id']
        region = server_cfg['region']

        if args.action == 'start':
            procs.append(Popen(
                ['aws', 'ec2', 'start-instances',
                 '--instance-ids', instance_id, '--region', region]))
        elif args.action == 'stop':
            procs.append(Popen(
                ['aws', 'ec2', 'stop-instances',
                 '--instance-ids', instance_id, '--region', region]))
        elif args.action == 'status':
            procs.append(Popen(
                ['aws', 'ec2', 'describe-instances',
                 '--instance-ids', instance_id, '--region', region,
                 '--query', 'Reservations[0].Instances[0].State.Name'],
                stdout=PIPE))

    for proc in procs:
        if args.action == 'status':
            status, _ = proc.communicate()
            sys.stdout.write(status.replace('"', ''))
        else:
            proc.wait()


if __name__ == '__main__':
    main()
