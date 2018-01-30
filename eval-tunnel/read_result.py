#!/usr/bin/env python

from os import path
import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('result')
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--scheme', default='default_tcp')
    args = parser.parse_args()

    data = {}
    data[args.scheme] = {}

    with open(args.result) as fh:
        for line in fh:
            if not line:
                break

            run_id, delay, tput = line.split()

            run_id = int(run_id)
            delay = float(delay)
            tput = float(tput)

            data[args.scheme][run_id] = {}
            data[args.scheme][run_id]['all'] = {}
            data[args.scheme][run_id]['all']['tput'] = tput
            data[args.scheme][run_id]['all']['delay'] = delay

    json_path = path.join(args.output_dir, 'pcap_data.json')
    with open(json_path, 'w') as fh:
        json.dump(data, fh)


if __name__ == '__main__':
    main()
