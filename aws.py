#!/usr/bin/env python

import sys
import argparse
from helpers.helpers import Popen, check_output, parse_config


def main():
    config = parse_config()

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    args = parser.parse_args()

    procs = []
    for server, server_cfg in config['aws_servers'].iteritems():
        instance_id = server_cfg['id']
        region = server_cfg['region']

        if args.action == 'start':
            procs.append(Popen(['aws', 'ec2', 'start-instances',
                         '--instance-ids', instance_id, '--region', region]))
        elif args.action == 'stop':
            procs.append(Popen(['aws', 'ec2', 'stop-instances',
                  '--instance-ids', instance_id, '--region', region]))
        elif args.action == 'status':
            status = check_output(
                    ['aws', 'ec2', 'describe-instances',
                     '--instance-ids', instance_id, '--region', region,
                     '--query', 'Reservations[0].Instances[0].State.Name'])
            sys.stdout.write(status.replace('"', ''))

    for proc in procs:
        proc.wait()


if __name__ == '__main__':
    main()
