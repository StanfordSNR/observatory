#!/usr/bin/env python

import sys
import os
from os import path
from datetime import datetime
from subprocess import Popen, PIPE, check_call, check_output
import argparse

sites = {
    'stanford': 'greg@171.66.3.239',
    'brazil': 'pi@177.234.144.122',
    'columbia': 'pi@138.121.201.58',
    'india': 'pi@109.73.164.122',
    'mexico': 'pi@143.255.56.146'
}

local_external_ip = '52.9.40.135'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('site_name', type=str, choices=sites.keys())
    args = parser.parse_args()

    test_dir = os.path.expanduser('~/pantheon/test/')
    os.chdir(test_dir)
    check_call('rm -f *.log', shell=True)
    check_call('rm -f *.pdf', shell=True)
    check_call('rm -f *.png', shell=True)
    check_call('rm -f *.xz ', shell=True)

    cmd = './run.py -t 30 -r ' + sites[args.site_name] + ':pantheon ' + \
          '--tunnel-server local --local-addr ' + local_external_ip + \
          ' --sender-side remote --remote-interface ppp0'
    print(cmd)
    check_call(cmd, shell=True)

    date = datetime.utcnow()
    date = date.replace(microsecond=0).isoformat().replace(':', '-')
    s3_url = 's3://stanford-pantheon/real-world-results/' + args.site_name \
             + '/'
    src_file = date + '_logs.xz'
    dst_file = s3_url + src_file
    check_call('tar caf ' + src_file + ' *.log', shell=True)
    check_call('aws s3 cp ' + src_file + ' ' + dst_file, shell=True)

    src_file = os.path.join(test_dir, 'pantheon_report.pdf')
    dst_file = s3_url + date + '_report.pdf'
    check_call('aws s3 cp ' + src_file + ' ' + dst_file, shell=True)

if __name__ == '__main__':
    main()
