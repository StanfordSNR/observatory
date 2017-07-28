#!/usr/bin/env python

import argparse
from helpers.helpers import call, parse_config


def main():
    config = parse_config()
    nodes = config['measurement_nodes'].keys() + config['cloud_servers'].keys()

    parser = argparse.ArgumentParser()
    parser.add_argument('server', choices=nodes)
    args = parser.parse_args()

    server = args.server

    for machine_type in config:
        if server in config[machine_type]:
            site = config[machine_type][server]
            host = site['user'] + '@' + site['addr']
            call(['ssh', host])


if __name__ == '__main__':
    main()
