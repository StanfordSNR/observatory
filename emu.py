#!/usr/bin/env python

import sys
import yaml
import argparse
from helpers.helpers import Popen, check_output, parse_config


def main():
    config = parse_config()

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    args = parser.parse_args()

    procs = []
    for server, server_cfg in config['emu_servers'].iteritems():
        instance_name = server_cfg['name']
        zone = server_cfg['zone']

        if args.action == 'start':
            procs.append(Popen(['gcloud', 'compute', 'instances', 'start',
                               instance_name, '--zone', zone]))
        elif args.action == 'stop':
            procs.append(Popen(['gcloud', 'compute', 'instances', 'stop',
                               instance_name, '--zone', zone]))
        elif args.action == 'status':
            d = yaml.load(check_output(
                    ['gcloud', 'compute', 'instances', 'describe',
                     instance_name, '--zone', zone]))
            sys.stdout.write(d['status'] + '\n')

    for proc in procs:
        proc.wait()


if __name__ == '__main__':
    main()
