#!/usr/bin/env python

import os
import sys
import argparse
from os import path
from datetime import datetime
from subprocess import check_call


def main():
    sources = {
        'AWS Brazil': '52.67.203.197',
        'AWS California': '52.52.80.245',
        'AWS Korea': '52.79.43.78',
    }

    destinations = {
        'Stanford': 'pi@171.67.76.32',
        'Brazil': 'pi@177.234.144.122',
        'Colombia': 'pi@138.121.201.58',
        'Mexico': 'pi@143.255.56.146',
        'China': 'yanyu@101.6.97.145'
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, choices=sources.keys())
    parser.add_argument('destination', type=str, choices=destinations.keys())
    parser.add_argument(
            '--run-times', metavar='TIMES', action='store', dest='run_times',
            type=int, default=1, help='run times of each test')
    args = parser.parse_args()

    test_dir = os.path.expanduser('~/pantheon/test/')
    os.chdir(test_dir)
    check_call('rm -rf *.log *.json *.png *.pdf *.out verus_tmp', shell=True)

    cmd = ('./run.py -r %s:~/pantheon -t 30 --tunnel-server local '
           '--local-addr %s --sender-side remote --remote-interface ppp0 '
           '--local-info "%s" --remote-info "%s" --random-order --run-times %s'
           % (destinations[args.destination], sources[args.source],
              args.source, args.destination, args.run_times))

    sys.stderr.write(cmd + ' --run-only setup\n')
    check_call(cmd + ' --run-only setup', shell=True)

    sys.stderr.write(cmd + ' --run-only test\n')
    check_call(cmd + ' --run-only test', shell=True)

    date = datetime.utcnow()
    date = date.replace(microsecond=0).isoformat().replace(':', '-')
    s3_url = 's3://stanford-pantheon/real-world-results/%s/' % args.destination
    src_dir = date + '_logs'
    check_call(['mkdir', src_dir])
    check_call('mv *.log *.json *.pdf' + src_dir, shell=True)

    src_archive = src_dir + '.tar.xz'
    check_call('tar cJf ' + src_archive + ' ' + src_dir, shell=True)

    dst_file = s3_url + src_archive
    check_call('aws s3 cp ' + src_archive + ' ' + dst_file, shell=True)

    sys.stderr.write('file uploaded to: %s\n' % dst_file)


if __name__ == '__main__':
    main()
