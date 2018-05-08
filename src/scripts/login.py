#!/usr/bin/env python

import argparse

import context
from helpers import utils
from helpers.subprocess_wrappers import call


def main():
    config = utils.parse_vantage_points()

    servers = []
    for server_type in config:
        servers += config[server_type].keys()

    parser = argparse.ArgumentParser()
    parser.add_argument('server', choices=servers)
    args = parser.parse_args()

    call(['ssh', utils.get_host_addr(args.server)])


if __name__ == '__main__':
    main()
