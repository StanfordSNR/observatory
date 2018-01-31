#!/usr/bin/env python

import sys
import json
import multiprocessing
import argparse
import pyshark
from os import path
import numpy as np


def worker(args, run_id, data):
    sys.stderr.write('{} is running\n'.format(run_id))

    send_pkts = {}
    send_pcap_name = '{scheme}-send-{run_id}.pcap'.format(
            scheme=args.scheme, run_id=run_id)
    send_pcap = pyshark.FileCapture(path.join(args.data_dir, send_pcap_name))

    for pkt in send_pcap:
        if pkt.ip.dst != args.receiver:
            continue

        if int(pkt.tcp.dstport) == 22:
            continue

        uid = pkt.tcp.seq
        ts = float(pkt.sniff_timestamp)
        size = int(pkt.ip.len)

        send_pkts[uid] = (ts, size)

    # calculate avg. tput
    first_ts = None
    last_ts = None
    total_size = 0

    # calculate 95th delay
    delays = []

    recv_pcap_name = '{scheme}-recv-{run_id}.pcap'.format(
            scheme=args.scheme, run_id=run_id)
    recv_pcap = pyshark.FileCapture(path.join(args.data_dir, recv_pcap_name))

    for pkt in recv_pcap:
        if pkt.ip.src != args.sender:
            continue

        if int(pkt.tcp.dstport) == 22:
            continue

        uid = pkt.tcp.seq
        ts = float(pkt.sniff_timestamp)

        if first_ts is None or ts < first_ts:
            first_ts = ts

        if last_ts is None or ts > last_ts:
            last_ts = ts

        size = int(pkt.ip.len)
        total_size += size

        if uid in send_pkts:
            delays.append(ts - send_pkts[uid][0])

    tput = 8.0 * total_size / (1000 * 1000 * (last_ts - first_ts))
    delay = 1000 * np.percentile(delays, 95, interpolation='nearest')

    print run_id, tput, delay

    data[args.scheme][run_id] = {}
    data[args.scheme][run_id]['all'] = {}
    data[args.scheme][run_id]['all']['tput'] = tput
    data[args.scheme][run_id]['all']['delay'] = delay

    data[args.scheme]['mean']['all']['tput'].append(tput)
    data[args.scheme]['mean']['all']['delay'].append(delay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sender', required=True)
    parser.add_argument('--receiver', required=True)
    parser.add_argument('--scheme', help='scheme to test', required=True)
    parser.add_argument('--data-dir', help='data dir', required=True)
    parser.add_argument('--run-times', type=int, required=True)
    args = parser.parse_args()

    data = {}
    data[args.scheme] = {}

    data[args.scheme]['mean'] = {}
    data[args.scheme]['mean']['all'] = {}
    data[args.scheme]['mean']['all']['tput'] = []
    data[args.scheme]['mean']['all']['delay'] = []

    jobs = []
    for run_id in range(1, args.run_times + 1):
        p = multiprocessing.Process(target=worker, args=(args, run_id, data))
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()


if __name__ == '__main__':
    main()
