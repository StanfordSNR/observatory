#!/usr/bin/env python

import os
from os import path
import sys
import json
import pickle
import argparse
import requests
from subprocess import check_call


class Console(object):
    pass


def compress(self, d):
    # compress logs
    for sender in d:
        cmd = 'cd {data_dir} && tar czvf {t}.tar.gz {t}'.format(
            data_dir=self.data_dir, t=d[sender]['title'])
        check_call(cmd, shell=True)

        d[sender]['tar'] = d[sender]['data_dir'] + '.tar.gz'


def analyze(self, d):
    analyze_cmd = '~/pantheon/analysis/analyze.py --data-dir %s >> %s 2>&1'

    for sender in d:
        cmd = analyze_cmd % (
            d[sender]['data_dir'], d[sender]['job_log'])
        check_call(cmd, shell=True)

        # load the pkl file to add to payload
        pkl_src = path.expanduser(
            path.join(d[sender]['data_dir'], 'perf_data.pkl'))

        with open(pkl_src) as pkl_file:
            d[sender]['perf_data'] = json.dumps(pickle.load(pkl_file))


def post_to_website(self, payload):
    sys.stderr.write('Posting results to website...\n')

    update_url = os.environ['UPDATE_URL']
    url = 'http://pantheon.stanford.edu/%s/%s/' % (
        update_url, self.expt_type)

    client = requests.session()
    response = client.get(url)

    csrftoken = client.cookies['csrftoken']
    payload['csrfmiddlewaretoken'] = csrftoken

    client.post(url, data=payload, headers=dict(Referer=url))


def upload(self, d):
    if self.expt_type == 'emu':
        s3_folder = 'stanford-pantheon/emulation/'
    else:
        slave_desc = self.slave['desc'].replace(' ', '-')
        s3_folder = 'stanford-pantheon/real-world/%s/' % slave_desc

    s3_base = 's3://' + s3_folder
    s3_reports = s3_base + 'reports/'
    s3_job_logs = s3_base + 'job-logs/'

    s3_url_base = 'https://s3.amazonaws.com/' + s3_folder
    s3_url_reports = s3_url_base + 'reports/'

    reports_to_upload = ['pantheon_report.pdf', 'pantheon_summary.svg',
                         'pantheon_summary_mean.svg']

    for sender in d:
        if self.expt_type == 'node':
            to_node = True if sender == 'local' else False

            if self.ppp0:
                link = 'cellular'
            else:
                if self.slave_name == 'nepal':
                    link = 'wireless'
                else:
                    link = 'ethernet'

            payload = {
                'cloud': self.master_name,
                'node': self.slave_name,
                'to_node': to_node,
                'link': link,
            }
        elif self.expt_type == 'cloud':
            if sender == 'local':
                src = self.master_name
                dst = self.slave_name
            else:
                src = self.slave_name
                dst = self.master_name

            payload = {
                'src': src,
                'dst': dst,
            }
        elif self.expt_type == 'emu':
            payload  = {
                'emu_cmd': self.mm_cmd,
                'desc': self.desc,
            }

        payload['flows'] = self.flows
        payload['runs'] = self.run_times
        payload['time_created'] = d[sender]['time']
        payload['perf_data'] = d[sender]['perf_data']

        # upload data logs
        data_logs = path.basename(d[sender]['tar'])

        cmd = 'aws s3 cp %s %s' % (
            d[sender]['tar'], path.join(s3_base, data_logs))
        check_call(cmd, shell=True)

        payload['log'] = path.join(s3_url_base, data_logs)

        # upload reports and job logs
        for report in reports_to_upload:
            src_path = path.join(d[sender]['data_dir'], report)

            dst_file = '%s-%s' % (
                d[sender]['title'], report.replace('_', '-'))
            dst_url = path.join(s3_reports, dst_file)

            cmd = 'aws s3 cp %s %s' % (src_path, dst_url)
            check_call(cmd, shell=True)

            # add s3 file to payload of POST request
            s3_url_file = path.join(s3_url_reports, dst_file)

            if report == 'pantheon_report.pdf':
                payload['report'] = s3_url_file
            elif report == 'pantheon_summary.svg':
                payload['graph1'] = s3_url_file
            elif report == 'pantheon_summary_mean.svg':
                payload['graph2'] = s3_url_file

        job_log = path.basename(d[sender]['job_log'])
        cmd = 'aws s3 cp %s %s' % (
            d[sender]['job_log'], path.join(s3_job_logs, job_log))
        check_call(cmd, shell=True)

        # post update to website
        post_to_website(self, payload)

    # remove data directories and tar
    cmd = 'rm -rf /tmp/pantheon-tmp'
    check_call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('saved_console')
    args = parser.parse_args()

    with open(args.saved_console, 'rb') as f:
        console = pickle.load(f)

    compress(console, console.d)

    analyze(console, console.d)

    upload(console, console.d)


if __name__ == '__main__':
    main()
