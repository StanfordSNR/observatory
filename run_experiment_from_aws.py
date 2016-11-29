#!/usr/bin/env python

import sys
import os
from os import path
from datetime import datetime
from subprocess import Popen, PIPE, check_call, check_output
import argparse

sources = {
    'AWS Brazil': '52.67.203.197',
    'AWS California': '52.52.80.245',
}

destinations = {
    'Stanford': 'pi@171.66.3.235',
    'Brazil': 'pi@177.234.144.122',
    'Colombia': 'pi@138.121.201.58',
    'India': 'pi@109.73.164.122',
    'Mexico': 'pi@143.255.56.146'
    'China': 'yanyu@101.6.97.145'
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, choices=sources.keys())
    parser.add_argument('destination', type=str, choices=destinations.keys())
    args = parser.parse_args()

    test_dir = os.path.expanduser('~/pantheon/test/')
    os.chdir(test_dir)

    local_head = check_output(['git', 'rev-parse', 'HEAD'])
    remote_head = check_output(['ssh', destinations[args.destination], 'git',
                                '-C', 'pantheon', 'rev-parse', 'HEAD'])
    assert (local_head == remote_head
            ), "pantheon versions differ between local (%s) and remote (%s)" \
        % (local_head[:-1], remote_head[:-1])

    check_call('rm -f *.log *.json', shell=True)

    cmd = './run.py -t 30 -r ' + destinations[args.destination] + ':pantheon '\
          '--tunnel-server local  --sender-side remote --random-order ' \
          '--local-addr ' + sources[args.source] + ' ' + \
          '--local-info "%s" ' % args.source + \
          '--remote-interface ppp0 --remote-info "%s" ' % args.destination + \
          '--run-times 10'

    print(cmd + ' --run-only setup')
    check_call(cmd + ' --run-only setup', shell=True)

    print(cmd + ' --run-only test')
    check_call(cmd + ' --run-only test', shell=True)

    date = datetime.utcnow()
    date = date.replace(microsecond=0).isoformat().replace(':', '-')
    s3_url = 's3://stanford-pantheon/real-world-results/' + args.destination \
             + '/'
    src_dir = date + '_logs'
    check_call(['mkdir', src_dir])
    check_call('mv *.log *.json ' + src_dir, shell=True)

    src_archive = src_dir + '.tar.xz'
    check_call('tar caf ' + src_archive + ' ' + src_dir, shell=True)

    dst_file = s3_url + src_archive
    check_call('aws s3 cp ' + src_archive + ' ' + dst_file, shell=True)

    print('file uploaded to: ' + dst_file)

if __name__ == '__main__':
    main()
