#!/usr/bin/env python

import argparse

import context
from helpers import utils


def get_hosts(args):
    config = utils.parse_vantage_points()

    hosts = []

    if args.hosts is not None:
        hosts = args.hosts.split()
    else:
        if args.all or args.nodes:
            for server in config['nodes']:
                hosts.append(server)

        if args.all or args.aws_servers:
            for server in config['aws_servers']:
                hosts.append(server)

        if args.all or args.gce_servers:
            for server in config['gce_servers']:
                hosts.append(server)

        if args.all or args.emu_servers:
            for server in config['emu_servers']:
                hosts.append(server)

    return hosts


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all', action='store_true',
        help='all hosts listed in vantange_points.yml')
    group.add_argument(
        '--nodes', action='store_true',
        help='all measurement nodes listed in vantange_points.yml')
    group.add_argument(
        '--aws-servers', action='store_true',
        help='all AWS servers listed in vantange_points.yml')
    group.add_argument(
        '--gce-servers', action='store_true',
        help='all GCE servers listed in vantange_points.yml')
    group.add_argument(
        '--emu-servers', action='store_true',
        help='all servers reserved for emulation listed in vantange_points.yml')
    group.add_argument(
        '--hosts', metavar='"HOST1 HOST2..."',
        help='space-separated list of hosts listed in vantange_points.yml')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ssh', metavar='CMD', help='commands to run over SSH')
    group.add_argument('--cmd', metavar='CMD', help='predefined commands')

    args = parser.parse_args()

    # obtain a list of host addresses (USER@IP)
    hosts = get_hosts(args)

    if args.ssh is not None:
        # run commands over SSH
        utils.simple_execute(hosts, args.ssh)
    else:
        # call the function with the name args.cmd
        getattr(utils, args.cmd)(hosts)


if __name__ == '__main__':
    main()
