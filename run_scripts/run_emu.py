#!/usr/bin/env python

import argparse
from os import path
import project_root
from helpers.helpers import Popen, check_call, wait_procs


def run_calibrated_emulators(base_cmd):
    procs = []

    # calibrated emulator: Nepal to AWS India
    cmd = base_cmd + ' --scenario 1 --id "Nepal to AWS India" --desc "Calibrated to the real path from Nepal to AWS India (http://pantheon.stanford.edu/result/188/)" --uplink-trace ~/traces/0.57mbps-poisson.trace --downlink-trace ~/traces/0.57mbps-poisson.trace --prepend-mm-cmds "mm-delay 28 mm-loss uplink 0.0477" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=14" emu_1'
    procs.append(Popen(cmd, shell=True))

    # calibrated emulator: Mexico ppp0 to AWS California
    cmd = base_cmd + ' --scenario 2 --id "Mexico ppp0 to AWS California" --desc "Calibrated to the real path from Mexico cellular to AWS California (http://pantheon.stanford.edu/result/196/)" --uplink-trace ~/traces/2.64mbps-poisson.trace --downlink-trace ~/traces/2.64mbps-poisson.trace --prepend-mm-cmds "mm-delay 88" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=130" emu_2'
    procs.append(Popen(cmd, shell=True))

    # calibrated emulator: AWS Brazil to Colombia ppp0
    cmd = base_cmd + ' --scenario 3 --id "AWS Brazil to Colombia ppp0" --desc "Calibrated to the real path from AWS Brazil to Colombia cellular (http://pantheon.stanford.edu/result/339/)" --uplink-trace ~/traces/3.04mbps-poisson.trace --downlink-trace ~/traces/3.04mbps-poisson.trace --prepend-mm-cmds "mm-delay 130" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=426" emu_3'
    procs.append(Popen(cmd, shell=True))

    # calibrated emulator: India to AWS India
    cmd = base_cmd + ' --scenario 4 --id "India to AWS India" --desc "Calibrated to the real path from India to AWS India (http://pantheon.stanford.edu/result/251/)" --uplink-trace ~/traces/100.42mbps.trace --downlink-trace ~/traces/100.42mbps.trace --prepend-mm-cmds "mm-delay 27" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=173" emu_4'
    procs.append(Popen(cmd, shell=True))

    # calibrated emulator: AWS Korea to China
    cmd = base_cmd + ' --scenario 5 --id "AWS Korea to China" --desc "Calibrated to the real path from AWS Korea to China (http://pantheon.stanford.edu/result/361/)" --uplink-trace ~/traces/77.72mbps.trace --downlink-trace ~/traces/77.72mbps.trace --prepend-mm-cmds "mm-delay 51 mm-loss uplink 0.0006" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=94" emu_5'
    procs.append(Popen(cmd, shell=True))

    # calibrated emulator: AWS California to Mexico
    cmd = base_cmd + ' --scenario 6 --id "AWS California to Mexico" --desc "Calibrated to the real path from AWS California to Mexico (http://pantheon.stanford.edu/result/353/)" --uplink-trace ~/traces/114.68mbps.trace --downlink-trace ~/traces/114.68mbps.trace --prepend-mm-cmds "mm-delay 45" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=450" emu_6'
    procs.append(Popen(cmd, shell=True))

    wait_procs(procs)


def run_google_scenarios(base_cmd):
    procs = []

    # scenario 1
    emu_id = 'token-bucket based policer 1'
    desc = 'Token-bucket based policer (bandwidth 12mbps, RTT 20ms)'
    cmd = base_cmd + ' --scenario 7 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/12mbps.trace --prepend-mm-cmds "mm-delay 10" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=1 --downlink-queue=droptail --downlink-queue-args=packets=1" emu_1' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'token-bucket based policer 2'
    desc = 'Token-bucket based policer (bandwidth 60mbps, RTT 20ms)'
    cmd = base_cmd + ' --scenario 8 --id "%s" --desc "%s" --uplink-trace ~/traces/60mbps.trace --downlink-trace ~/traces/60mbps.trace --prepend-mm-cmds "mm-delay 10" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=1 --downlink-queue=droptail --downlink-queue-args=packets=1" emu_2' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'token-bucket based policer 3'
    desc = 'Token-bucket based policer (bandwidth 108mbps, RTT 20ms)'
    cmd = base_cmd + ' --scenario 9 --id "%s" --desc "%s" --uplink-trace ~/traces/108mbps.trace --downlink-trace ~/traces/108mbps.trace --prepend-mm-cmds "mm-delay 10" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=1 --downlink-queue=droptail --downlink-queue-args=packets=1" emu_3' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'token-bucket based policer 4'
    desc = 'Token-bucket based policer (bandwidth 12mbps, RTT 100ms)'
    cmd = base_cmd + ' --scenario 10 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/12mbps.trace --prepend-mm-cmds "mm-delay 50" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=1 --downlink-queue=droptail --downlink-queue-args=packets=1" emu_4' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'token-bucket based policer 5'
    desc = 'Token-bucket based policer (bandwidth 60mbps, RTT 100ms)'
    cmd = base_cmd + ' --scenario 11 --id "%s" --desc "%s" --uplink-trace ~/traces/60mbps.trace --downlink-trace ~/traces/60mbps.trace --prepend-mm-cmds "mm-delay 50" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=1 --downlink-queue=droptail --downlink-queue-args=packets=1" emu_5' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'token-bucket based policer 6'
    desc = 'Token-bucket based policer (bandwidth 108mbps, RTT 100ms)'
    cmd = base_cmd + ' --scenario 12 --id "%s" --desc "%s" --uplink-trace ~/traces/108mbps.trace --downlink-trace ~/traces/108mbps.trace --prepend-mm-cmds "mm-delay 50" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=1 --downlink-queue=droptail --downlink-queue-args=packets=1" emu_6' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    wait_procs(procs)

    # scenario 2
    procs = []

    emu_id = 'severe ACK aggregation 1'
    desc = 'Severe ACK aggregation (1 ACK every 100ms)'
    cmd = base_cmd + ' --scenario 13 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/0.12mbps.trace --prepend-mm-cmds "mm-delay 10" emu_1' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'severe ACK aggregation 2'
    desc = 'Severe ACK aggregation (10 ACKs every 200ms)'
    cmd = base_cmd + ' --scenario 14 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/10-every-200.trace --prepend-mm-cmds "mm-delay 10" emu_2' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    # scenario 3
    emu_id = 'bottleneck buffer 1'
    desc = 'Bottleneck buffer = BDP/10'
    cmd = base_cmd + ' --scenario 15 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/12mbps.trace --prepend-mm-cmds "mm-delay 30" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=bytes=9000" emu_3' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'bottleneck buffer 2'
    desc = 'Bottleneck buffer = BDP/3'
    cmd = base_cmd + ' --scenario 16 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/12mbps.trace --prepend-mm-cmds "mm-delay 30" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=bytes=30000" emu_4' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'bottleneck buffer 3'
    desc = 'Bottleneck buffer = BDP/2'
    cmd = base_cmd + ' --scenario 17 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/12mbps.trace --prepend-mm-cmds "mm-delay 30" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=bytes=45000" emu_5' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    emu_id = 'bottleneck buffer 4'
    desc = 'Bottleneck buffer = BDP'
    cmd = base_cmd + ' --scenario 18 --id "%s" --desc "%s" --uplink-trace ~/traces/12mbps.trace --downlink-trace ~/traces/12mbps.trace --prepend-mm-cmds "mm-delay 30" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=bytes=90000" emu_6' % (emu_id, desc)
    procs.append(Popen(cmd, shell=True))

    wait_procs(procs)


def run(args):
    assistant = path.join(project_root.DIR, 'assistant.py')
    console = path.join(project_root.DIR, 'console.py')

    check_call([assistant, '--emu-servers', '-c', 'cleanup'])
    check_call([assistant, '--emu-servers', '-c', 'setup'])

    base_cmd = '%s emu --schemes "bbr default_tcp ledbat pcc quic scream webrtc sprout taova vegas verus copa fillp indigo indigo_no_calibration vivace_latency vivace_loss vivace_lte" --run-times 10' % console
    if args.flows > 1:
        base_cmd += ' -f %s' % args.flows

    if args.calibrated_emulators:
        run_calibrated_emulators(base_cmd)

    if args.google_scenarios:
        run_google_scenarios(base_cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--flows', metavar='FLOWS', type=int, default=1,
        help='number of flows (default 1)')
    parser.add_argument('--google-scenarios', action='store_true',
                        help='run google scenarios')
    parser.add_argument('--calibrated-emulators', action='store_true',
                        help='run calibrated emulators')
    args = parser.parse_args()

    run(args)


if __name__ == '__main__':
    main()
