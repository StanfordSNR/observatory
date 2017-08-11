#!/usr/bin/env python

import argparse
from os import path
import project_root
from helpers.helpers import Popen, check_call, wait_procs


def run(args):
    assistant = path.join(project_root.DIR, 'assistant.py')
    console = path.join(project_root.DIR, 'console.py')

    mappings = {
        'stanford': 'aws_california_1',
        'mexico': 'aws_california_2',
        'brazil': 'aws_brazil_1',
        'colombia': 'aws_brazil_2',
        'india': 'aws_india_1',
        'china': 'aws_korea',
        'nepal': 'aws_india_2',
    }

    if args.ppp0:
        nodes = ['stanford', 'mexico', 'brazil', 'colombia', 'india', 'china']
    else:
        nodes = mappings.keys()

    # setup
    if 'nepal' in nodes:
        check_call([assistant, '--hosts', 'nepal', '-c', 'mount_readwrite'])

    hosts = []
    for node in nodes:
        hosts.append(node)
        hosts.append(mappings[node])
    hosts = ','.join(hosts)

    check_call([assistant, '--hosts', hosts, '-c', 'cleanup'])
    check_call([assistant, '--hosts', hosts, '-c', 'setup'])

    if args.ppp0:
        check_call([assistant, '--hosts', ','.join(nodes), '-c', 'setup_ppp0'])

    # run experiments
    if args.ppp0:
        base_cmd = [console, 'node', '--run-times', '3', '--ppp0']
    else:
        base_cmd = [console, 'node', '--run-times', '10']

    if args.flows > 1:
        base_cmd += ['-f', str(args.flows)]

    procs = []

    for node in nodes:
        if node == 'nepal':
            procs.append(Popen(base_cmd + ['--schemes', 'default_tcp vegas ledbat pcc verus sprout quic scream webrtc copa taova koho_cc calibrated_koho saturator', mappings['nepal'], 'nepal']))
        else:
            procs.append(Popen(base_cmd + ['--all', mappings[node], node]))

    wait_procs(procs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--flows', metavar='FLOWS', type=int, default=1,
        help='number of flows (default 1)')
    parser.add_argument(
        '--ppp0', action='store_true', help='use ppp0 interface on node')
    args = parser.parse_args()

    run(args)


if __name__ == '__main__':
    main()
