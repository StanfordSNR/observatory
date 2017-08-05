#!/usr/bin/env python

import os
import argparse
from helpers.helpers import (check_call, call, Popen, parse_config,
                             run_cmd_on_hosts)
from helpers.commands import (clone_setup, git_pull, pkill, setup, setup_ppp0,
                              add_pub_key, ssh_each_other)


def get_hosts(args):
    config = parse_config()

    host_names = []

    if args.hosts is not None:
        host_names = args.hosts.split(',')
    else:
        if args.all or args.nodes:
            for server in config['nodes']:
                host_names.append(server)

        if args.all or args.aws_servers:
            for server in config['aws_servers']:
                host_names.append(server)

        if args.all or args.gce_servers:
            for server in config['gce_servers']:
                host_names.append(server)

    hosts = []
    for server_type in config:
        for server in config[server_type]:
            if server in host_names:
                server_cfg = config[server_type][server]
                hosts.append(server_cfg['user'] + '@' + server_cfg['addr'])

    return hosts


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all', action='store_true',
        help='all hosts listed in config.yml')
    group.add_argument(
        '--nodes', action='store_true',
        help='all measurement nodes listed in config.yml')
    group.add_argument(
        '--aws-servers', action='store_true',
        help='all AWS servers listed in config.yml')
    group.add_argument(
        '--gce-servers', action='store_true',
        help='all GCE servers listed in config.yml')
    group.add_argument(
        '--hosts', metavar='"HOST1,HOST2..."',
        help='comma-separated list of hosts listed in config.yml')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ssh', metavar='CMD', help='commands to run over SSH')
    group.add_argument('-c', metavar='CMD', help='predefined commands')

    args = parser.parse_args()

    # obtain a list of host addresses (USER@IP)
    hosts = get_hosts(args)

    if args.ssh is not None:
        # run commands over SSH
        run_cmd_on_hosts(args.ssh, hosts)
    else:
        # call the function with the name args.c
        globals()[args.c](hosts)


if __name__ == '__main__':
    main()
