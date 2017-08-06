#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import Popen, check_call, wait_procs


def main():
    assistant = path.join(project_root.DIR, 'assistant.py')
    console = path.join(project_root.DIR, 'console.py')

    check_call([assistant, '--aws-servers', '-c', 'pkill'])
    check_call([assistant, '--aws-servers', '-c', 'setup'])

    base_cmd = [console, 'emu', '--all', '--run-times', '10']

    procs = []

    # China cellular to AWS Korea
    cmd =  base_cmd + ['--id', 'China ppp0 to AWS Korea', '--desc', 'Calibrated to the real path from China cellular to AWS Korea (2016-12-30T21-38-China-ppp0-to-AWS-Korea-10-runs)', '--uplink-trace', '~/pantheon/test/6.25mbps.trace', '--downlink-trace', '~/pantheon/test/6.25mbps.trace', '--prepend-mm-cmds', 'mm-delay 152 mm-loss uplink 0.0025', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=362', 'aws_korea']
    procs.append(Popen(cmd))

    # AWS Brazil to Brazil
    cmd =  base_cmd + ['--id', 'AWS Brazil to Brazil', '--desc', 'Calibrated to the real path from AWS Brazil to Brazil (2017-01-04T07-24-AWS-Brazil-1-to-Brazil-10-runs)', '--uplink-trace', '~/pantheon/test/97.11mbps.trace', '--downlink-trace', '~/pantheon/test/97.11mbps.trace', '--prepend-mm-cmds', 'mm-delay 1', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=366', 'aws_brazil_1']
    procs.append(Popen(cmd))

    # AWS Brazil to Colombia cellular
    cmd =  base_cmd + ['--id', 'AWS Brazil to Colombia ppp0', '--desc', 'Calibrated to the real path from AWS Brazil to Colombia cellular (2016-12-30T22-50-AWS-Brazil-2-to-Colombia-ppp0-10-runs)', '--uplink-trace', '~/pantheon/test/5.65mbps.trace', '--downlink-trace', '~/pantheon/test/5.65mbps.trace', '--prepend-mm-cmds', 'mm-delay 88 mm-loss uplink 0.0026 mm-loss downlink 0.0001', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=3665', 'aws_brazil_2']
    procs.append(Popen(cmd))

    # India to AWS India
    cmd =  base_cmd + ['--id', 'India to AWS India', '--desc', 'Calibrated to the real path from India to AWS India (2017-01-02T03-54-India-to-AWS-India-10-runs)', '--uplink-trace', '~/pantheon/test/117.65mbps.trace', '--downlink-trace', '~/pantheon/test/117.65mbps.trace', '--prepend-mm-cmds', 'mm-delay 13', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=144', 'aws_india_1']
    procs.append(Popen(cmd))

    # Nepal to AWS India
    cmd =  base_cmd + ['--id', 'Nepal to AWS India', '--desc', 'Calibrated to the real path from Nepal to AWS India (2017-01-03T21-30-Nepal-to-AWS-India-10-runs)', '--uplink-trace', '~/pantheon/test/13.38mbps.trace', '--downlink-trace', '~/pantheon/test/13.38mbps.trace', '--prepend-mm-cmds', 'mm-delay 32 mm-loss uplink 0.003', '--extra-mm-link-args', '--uplink-queue=droptail --uplink-queue-args=packets=37', 'aws_india_2']
    procs.append(Popen(cmd))

    wait_procs(procs)


if __name__ == '__main__':
    main()
