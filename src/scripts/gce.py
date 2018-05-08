#!/usr/bin/env python

import argparse
import yaml

import context
from  helpers import utils
from helpers.subprocess_wrappers import Popen, check_output, PIPE


def main():
    config = utils.parse_vantage_points()

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    parser.add_argument('server_type', choices=['gce_servers', 'emu_servers'])
    args = parser.parse_args()

    procs = []
    for server, server_cfg in config[args.server_type].iteritems():
        instance_name = server_cfg['name']
        zone = server_cfg['zone']

        if args.action == 'start':
            procs.append(Popen(
                ['gcloud', 'compute', 'instances', 'start',
                 instance_name, '--zone', zone]))
        elif args.action == 'stop':
            procs.append(Popen(
                ['gcloud', 'compute', 'instances', 'stop',
                 instance_name, '--zone', zone]))
        elif args.action == 'status':
            procs.append(Popen(
                ['gcloud', 'compute', 'instances', 'describe',
                 instance_name, '--zone', zone],
                stdout=PIPE))

    for proc in procs:
        if args.action == 'status':
            status, _ = proc.communicate()
            print(yaml.load(status)['status'])
        else:
            proc.wait()


if __name__ == '__main__':
    main()
