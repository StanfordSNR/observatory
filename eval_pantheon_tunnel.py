#!/usr/bin/env python

import time
import argparse
from helpers.helpers import parse_config, get_open_port, check_call, Popen


def run_tunnel(run_id, args, local, remote):
    # apply patch
    src = '~/pantheon/src/{}.py'.format(args.scheme)
    check_call(src + ' setup', shell=True)
    check_call(src + ' setup_after_reboot', shell=True)

    tunnel_cmd = (
        '~/pantheon/test/test.py remote {remote_host}:~/pantheon '
        '--schemes {scheme} -t 30 --start-run-id {run_id} --run-times 1 -f 1 '
        '--tunnel-server local --local-addr {local_addr} '
        '--local-desc "{local_desc}" --remote-desc "{remote_desc}" '
        '--pkill-cleanup --sender local --data-dir {data_dir}').format(
        remote_host=remote['user'] + '@' + remote['addr'],
        scheme=args.scheme,
        run_id=run_id,
        local_addr=local['addr'],
        local_desc=local['desc'],
        remote_desc=remote['desc'],
        data_dir=args.data_dir)

    check_call(tunnel_cmd, shell=True)


def run_no_tunnel(run_id, args, local, remote):
    # reset patch
    if args.scheme == 'pcc' or args.scheme == 'verus' or args.scheme == 'sprout':
        check_call('cd ~/pantheon/third_party/{} && git reset --hard master'.format(args.scheme), shell=True)

    remote_host = remote['user'] + '@' + remote['addr']

    procs = []

    # run tcpdump
    cmd = ('sudo tcpdump -n -i {local_if} dst {remote_addr} '
           '-w {data_dir}/{scheme}-send-{run_id}.pcap').format(
           local_if=local['interface'],
           remote_addr=remote['addr'],
           data_dir=args.data_dir,
           scheme=args.scheme,
           run_id=run_id)
    procs.append(Popen(cmd, shell=True))

    cmd = ('ssh {remote_host} "sudo tcpdump -n -i {remote_if} '
           'src {local_addr} -w /tmp/{scheme}-recv-{run_id}.pcap"').format(
           remote_host=remote_host,
           remote_if=remote['interface'],
           local_addr=local['addr'],
           data_dir=args.data_dir,
           scheme=args.scheme,
           run_id=run_id)
    procs.append(Popen(cmd, shell=True))

    # run receiver
    src = '~/pantheon/src/{}.py'.format(args.scheme)

    port = get_open_port()
    cmd = 'ssh {remote_host} "{src} receiver {port}"'.format(
          src=src, remote_host=remote_host, port=port)
    procs.append(Popen(cmd, shell=True))

    # wait for the receiver to be ready
    time.sleep(3)

    # run sender
    cmd = '{src} sender {remote_addr} {port}'.format(
          src=src, remote_addr=remote['addr'], port=port)
    procs.append(Popen(cmd, shell=True))

    # run both sides for (roughly) 30 seconds
    time.sleep(30)

    # cleanup
    for proc in procs:
        if proc:
            proc.kill()

    cmd = 'ssh {remote_host} "sudo pkill -f tcpdump; pkill -f {src}"'.format(
          remote_host=remote_host, src=src)
    check_call(cmd, shell=True)
    cmd = 'sudo pkill -f tcpdump; pkill -f {src}'.format(src=src)
    check_call(cmd, shell=True)

    # copy back pcap file
    cmd = 'scp {remote_host}:/tmp/{scheme}-recv-{run_id}.pcap {data_dir}'.format(
          remote_host=remote_host,
          scheme=args.scheme,
          run_id=run_id,
          data_dir=args.data_dir)
    check_call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('local', help='local side')
    parser.add_argument('remote', help='remote side')
    parser.add_argument('--scheme', help='scheme to test')
    parser.add_argument('--data-dir', help='data dir')
    args = parser.parse_args()

    config = parse_config()

    if args.local in config['aws_servers']:
        local = config['aws_servers'][args.local]
    elif args.local in config['nodes']:
        local = config['nodes'][args.local]

    if args.remote in config['aws_servers']:
        remote = config['aws_servers'][args.remote]
    elif args.remote in config['nodes']:
        remote = config['nodes'][args.remote]

    for run_id in xrange(1, 2):
        run_tunnel(run_id, args, local, remote)
        run_no_tunnel(run_id, args, local, remote)


if __name__ == '__main__':
    main()
