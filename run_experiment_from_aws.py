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

    local_head = check_output(['git', 'rev-parse', 'HEAD'])
    remote_head = check_output(['ssh', sites[args.site_name], 'git', '-C', 'pantheon', 'rev-parse', 'HEAD'])
    assert local_head == remote_head, "pantheon versions differ between local (%s) and remote (%s)" % (local_head[:-1], remote_head[:-1])

    local_submodules = check_output(['git', 'submodule', 'summary'])
    remote_submodules = check_output(['ssh', sites[args.site_name], 'git', '-C', 'pantheon', 'submodule', 'summary'])
    assert local_submodules == remote_submodules, "pantheon submodule versions differ between local and remote repositories"

    check_call('rm -f *.log', shell=True)
    check_call('rm -f *.pdf', shell=True)
    check_call('rm -f *.png', shell=True)
    check_call('rm -f *.xz ', shell=True)

    cmd = './run.py -t 10 -r ' + sites[args.site_name] + ':pantheon ' + \
          '--tunnel-server local --local-addr ' + local_external_ip + \
          ' --sender-side remote --remote-interface ppp0 ' \
          '--local-info aws_california --remote-info ' + args.site_name

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
