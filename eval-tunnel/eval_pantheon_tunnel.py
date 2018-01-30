#!/usr/bin/env python

import time
import argparse
import project_root
from helpers.helpers import get_open_port, check_call, call, Popen


def run_tunnel(run_id, args):
    tunnel_cmd = (
        '~/pantheon/test/test.py remote {remote_host}:~/pantheon '
        '--schemes {scheme} -t 30 --start-run-id {run_id} --run-times 1 '
        '--tunnel-server local --local-addr {local_addr} '
        '--pkill-cleanup --sender local --data-dir {data_dir}').format(
        remote_host=args['remote_host'],
        scheme=args['scheme'],
        run_id=run_id,
        local_addr=args['local_addr'],
        data_dir=args['data_dir'])

    check_call(tunnel_cmd, shell=True)


def run_no_tunnel(run_id, args):
    procs = []

    port = get_open_port()

    # run tcpdump
    cmd = ('sudo tcpdump -n -s 96 -i {local_if} dst {remote_addr} '
           'and dst port {remote_port} '
           '-w {data_dir}/{scheme}-send-{run_id}.pcap').format(
           local_if=args['local_if'],
           remote_addr=args['remote_addr'],
           remote_port=port,
           data_dir=args['data_dir'],
           scheme=args['scheme'],
           run_id=run_id)
    procs.append(Popen(cmd, shell=True))

    cmd = ('ssh {remote_host} "sudo tcpdump -n -s 96 -i {remote_if} '
           'src {local_addr} and dst port {remote_port} '
           '-w /tmp/{scheme}-recv-{run_id}.pcap"').format(
           remote_host=args['remote_host'],
           remote_if=args['remote_if'],
           local_addr=args['local_addr'],
           remote_port=port,
           scheme=args['scheme'],
           run_id=run_id)
    procs.append(Popen(cmd, shell=True))

    # run receiver
    src = '~/pantheon/src/{}.py'.format(args['scheme'])

    cmd = 'ssh {remote_host} "{src} receiver {port}"'.format(
          src=src, remote_host=args['remote_host'], port=port)
    procs.append(Popen(cmd, shell=True))

    # wait for the receiver to be ready
    time.sleep(2)

    # run sender
    cmd = '{src} sender {remote_addr} {port}'.format(
          src=src, remote_addr=args['remote_addr'], port=port)
    procs.append(Popen(cmd, shell=True))

    # run both sides for (roughly) 30 seconds
    time.sleep(30)

    # cleanup
    for proc in procs:
        if proc:
            proc.kill()

    pkill_cmd = "sudo pkill -f tcpdump; pkill -f iperf"
    cmd = 'ssh {remote_host} "{pkill_cmd}"'.format(
            remote_host=args['remote_host'], pkill_cmd=pkill_cmd)
    call(cmd, shell=True)
    call(pkill_cmd, shell=True)

    # copy back pcap file
    cmd = 'scp {remote_host}:/tmp/{scheme}-recv-{run_id}.pcap {data_dir}'.format(
          remote_host=args['remote_host'],
          scheme=args['scheme'],
          run_id=run_id,
          data_dir=args['data_dir'])
    check_call(cmd, shell=True)

    # remote pcap file on remote
    cmd = 'ssh {remote_host} "sudo rm -f /tmp/{scheme}-recv-{run_id}.pcap"'.format(
          remote_host=args['remote_host'],
          scheme=args['scheme'],
          run_id=run_id)
    call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-host', help='local_user@local_addr')
    parser.add_argument('--remote-host', help='remote_user@remote_addr')
    parser.add_argument('--local-if', help='local interface')
    parser.add_argument('--remote-if', help='remote interface')
    parser.add_argument('--scheme', help='scheme to test', default='default_tcp')
    parser.add_argument('--data-dir', help='data dir')
    prog_args = parser.parse_args()

    args = {}
    args['local_host'] = prog_args.local_host
    args['remote_host'] = prog_args.remote_host
    args['local_if'] = prog_args.local_if
    args['remote_if'] = prog_args.remote_if
    args['scheme'] = prog_args.scheme
    args['data_dir'] = prog_args.data_dir
    args['local_addr'] = args['local_host'].split('@')[1]
    args['remote_addr'] = args['remote_host'].split('@')[1]

    # disable TSO/GSO/GRO on both ends
    print('Please run: sudo ethtool -K <interface> tso off; '
          'sudo ethtool -K <interface> gso off; '
          'sudo ethtool -K <interface> gro off')

    # set recv buffer
    print('Please run: sudo sysctl -w net.core.rmem_max="33554432"; '
          'sudo sysctl -w net.core.rmem_default="16777216"')

    for run_id in xrange(1, 101):
        run_tunnel(run_id, args)
        run_no_tunnel(run_id, args)


if __name__ == '__main__':
    main()
