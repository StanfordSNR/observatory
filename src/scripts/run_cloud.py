#!/usr/bin/env python

import argparse
from os import path
import project_root
from helpers.helpers import Popen, check_call, wait_procs


def run(args):
    assistant = path.join(project_root.DIR, 'assistant.py')
    console = path.join(project_root.DIR, 'console.py')

    check_call([assistant, '--gce-servers', '-c', 'cleanup'])
    check_call([assistant, '--gce-servers', '-c', 'setup'])

    base_cmd = [console, 'cloud', '--schemes', 'bbr default_tcp ledbat pcc quic scream webrtc sprout taova vegas verus copa fillp indigo_1_32 indigo_1_32_no_calib vivace pcc_experimental', '--run-times', '10']

    if args.flows > 1:
        base_cmd += ['-f', str(args.flows)]

    # first round
    procs = []
    procs.append(Popen(base_cmd + ['gce_iowa', 'gce_sydney']))
    procs.append(Popen(base_cmd + ['gce_london', 'gce_tokyo']))
    wait_procs(procs)

    # second round
    procs = []
    procs.append(Popen(base_cmd + ['gce_iowa', 'gce_london']))
    procs.append(Popen(base_cmd + ['gce_sydney', 'gce_tokyo']))
    wait_procs(procs)

    # third round
    procs = []
    procs.append(Popen(base_cmd + ['gce_iowa', 'gce_tokyo']))
    procs.append(Popen(base_cmd + ['gce_sydney', 'gce_london']))
    wait_procs(procs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--flows', metavar='FLOWS', type=int, default=1,
        help='number of flows (default 1)')
    args = parser.parse_args()

    run(args)


if __name__ == '__main__':
    main()
