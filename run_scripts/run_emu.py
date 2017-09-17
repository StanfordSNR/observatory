#!/usr/bin/env python

import argparse
from os import path
import project_root
from helpers.helpers import Popen, check_call, wait_procs


def run(args):
    assistant = path.join(project_root.DIR, 'assistant.py')
    console = path.join(project_root.DIR, 'console.py')

    check_call([assistant, '--emu-servers', '-c', 'cleanup'])
    check_call([assistant, '--emu-servers', '-c', 'setup'])

    base_cmd = [console, 'emu', '--all', '--run-times', '10']
    if args.flows > 1:
        base_cmd += ['-f', str(args.flows)]

    procs = []

    # Nepal to AWS India
    cmd =  base_cmd + ['--id', 'Nepal to AWS India', '--desc', 'Calibrated to the real path from Nepal to AWS India (http://pantheon.stanford.edu/result/188/)', '--uplink-trace', '~/pantheon/test/0.57mbps-poisson.trace', '--downlink-trace', '~/pantheon/test/0.57mbps-poisson.trace', '--prepend-mm-cmds', 'mm-delay 28 mm-loss uplink 0.0477', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=14', 'emu_1']
    procs.append(Popen(cmd))

    # Mexico ppp0 to AWS California
    cmd =  base_cmd + ['--id', 'Mexico ppp0 to AWS California', '--desc', 'Calibrated to the real path from Mexico cellular to AWS California (http://pantheon.stanford.edu/result/196/)', '--uplink-trace', '~/pantheon/test/2.64mbps-poisson.trace', '--downlink-trace', '~/pantheon/test/2.64mbps-poisson.trace', '--prepend-mm-cmds', 'mm-delay 88', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=130', 'emu_2']
    procs.append(Popen(cmd))

    # AWS Brazil to Colombia ppp0
    cmd =  base_cmd + ['--id', 'AWS Brazil to Colombia ppp0', '--desc', 'Calibrated to the real path from AWS Brazil to Colombia cellular (http://pantheon.stanford.edu/result/339/)', '--uplink-trace', '~/pantheon/test/3.04mbps-poisson.trace', '--downlink-trace', '~/pantheon/test/3.04mbps-poisson.trace', '--prepend-mm-cmds', 'mm-delay 130', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=426', 'emu_3']
    procs.append(Popen(cmd))

    # India to AWS India
    cmd =  base_cmd + ['--id', 'India to AWS India', '--desc', 'Calibrated to the real path from India to AWS India (http://pantheon.stanford.edu/result/251/)', '--uplink-trace', '~/pantheon/test/100.42mbps.trace', '--downlink-trace', '~/pantheon/test/100.42mbps.trace', '--prepend-mm-cmds', 'mm-delay 27', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=173', 'emu_4']
    procs.append(Popen(cmd))

    # AWS Korea to China
    cmd =  base_cmd + ['--id', 'AWS Korea to China', '--desc', 'Calibrated to the real path from AWS Korea to China (http://pantheon.stanford.edu/result/361/)', '--uplink-trace', '~/pantheon/test/77.72mbps.trace', '--downlink-trace', '~/pantheon/test/77.72mbps.trace', '--prepend-mm-cmds', 'mm-delay 51 mm-loss uplink 0.0006', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=94', 'emu_5']
    procs.append(Popen(cmd))

    # AWS California to Mexico
    cmd =  base_cmd + ['--id', 'AWS California to Mexico', '--desc', 'Calibrated to the real path from AWS California to Mexico (http://pantheon.stanford.edu/result/353/)', '--uplink-trace', '~/pantheon/test/114.68mbps.trace', '--downlink-trace', '~/pantheon/test/114.68mbps.trace', '--prepend-mm-cmds', 'mm-delay 45', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=450', 'emu_6']
    procs.append(Popen(cmd))

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
