#!/usr/bin/env python

import argparse
from helpers.helpers import call, parse_config


def main():
    config = parse_config()

    servers = []
    for server_type in config:
        servers += config[server_type].keys()

    parser = argparse.ArgumentParser()
    parser.add_argument('server', choices=servers)
    args = parser.parse_args()

    server = args.server

    for server_type in config:
        if server in config[server_type]:
            server_cfg = config[server_type][server]
            host = server_cfg['user'] + '@' + server_cfg['addr']
            call(['ssh', host])


if __name__ == '__main__':
    main()
