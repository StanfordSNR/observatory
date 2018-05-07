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
    }

    if args.ppp0:
        nodes = ['stanford', 'colombia', 'india']
    else:
        nodes = ['stanford', 'mexico', 'brazil', 'colombia', 'india', 'china']

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
        procs.append(Popen(base_cmd + ['--schemes', 'bbr default_tcp ledbat pcc quic scream webrtc sprout taova vegas verus copa fillp indigo_1_32 indigo_1_32_no_calib vivace pcc_experimental', mappings[node], node]))

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
