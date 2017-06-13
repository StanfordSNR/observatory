#!/usr/bin/env python

import os
from os import path
import argparse
import requests
from helpers.helpers import parse_config, check_call, utc_date


class Console(object):
    def __init__(self, args, config):
        self.measurement_node = args.measurement_node
        self.run_times = args.run_times

        self.server = config['cloud_servers'][args.cloud_server]
        self.node = config['measurement_nodes'][args.measurement_node]

        self.ppp0 = args.ppp0
        if self.ppp0:
            self.link = 'cellular'
        else:
            if 'nepal' in self.measurement_node:
                self.link = 'wireless'
            else:
                self.link = 'ethernet'

        self.server_host = '%s@%s' % (self.server['user'], self.server['addr'])
        self.node_host = '%s@%s' % (self.node['user'], self.node['addr'])
        self.ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                        self.server_host]

        if args.all:
            self.schemes = '--all'
        elif args.schemes is not None:
            self.schemes = '--schemes "%s"' % args.schemes

        self.pdata = '~/pantheon_data'
        cmd = 'mkdir -p ' + self.pdata
        check_call(self.ssh_cmd + [cmd])

    def test(self):
        common_cmd = (
            '~/pantheon/test/test.py remote {s.node_host}:~/pantheon '
            '{s.schemes} --random-order -t 30 --run-times {s.run_times} '
            '--tunnel-server local --local-addr {s.server[addr]} '
            '--local-desc "{s.server[desc]}" --remote-desc "{s.node[desc]}" '
            '--ntp-addr {s.server[ntp]} --pkill-cleanup').format(s=self)

        title_node_desc = self.node['desc']
        if self.ppp0:
            common_cmd += ' --remote-if ppp0'
            title_node_desc += ' ppp0'

        runs_str = 'runs' if self.run_times > 1 else 'run'
        expt_title = '%s to %s' + ' %d %s' % (self.run_times, runs_str)

        d = {}

        # run experiments
        for sender in ['local', 'remote']:
            d[sender] = {}
            if sender == 'local':
                title = expt_title % (self.server['desc'], title_node_desc)
            else:
                title = expt_title % (title_node_desc, self.server['desc'])

            title = title.replace(' ', '-')
            d[sender]['time'] = utc_date()
            d[sender]['title'] = '%s-%s' % (d[sender]['time'], title)

            d[sender]['data_dir'] = path.join(self.pdata, d[sender]['title'])
            d[sender]['job_log'] = path.join(
                self.pdata, '%s.log' % d[sender]['title'])

            cmd = common_cmd + ' --sender %s --data-dir %s >> %s 2>&1' % (
                sender, d[sender]['data_dir'], d[sender]['job_log'])
            check_call(self.ssh_cmd + [cmd])

        # compress logs
        for sender in ['local', 'remote']:
            cmd = 'cd {pdata} && tar cJf {t}.tar.xz {t}'.format(
                pdata=self.pdata, t=d[sender]['title'])
            check_call(self.ssh_cmd + [cmd])

            d[sender]['tar'] = d[sender]['data_dir'] + '.tar.xz'

        return d

    def analyze(self, d):
        analyze_cmd = '~/pantheon/analysis/analyze.py --data-dir %s >> %s 2>&1'

        for sender in ['local', 'remote']:
            cmd = analyze_cmd % (
                d[sender]['data_dir'], d[sender]['job_log'])
            check_call(self.ssh_cmd + [cmd])

    def post_to_website(self, payload):
        update_url = os.environ['UPDATE_URL']
        url = 'http://pantheon.stanford.edu/%s/' % update_url

        client = requests.session()
        response = client.get(url)

        csrftoken = client.cookies['csrftoken']
        payload['csrfmiddlewaretoken'] = csrftoken

        client.post(url, data=payload, headers=dict(Referer=url))

    def upload(self, d):
        node_desc = self.node['desc'].replace(' ', '-')
        s3_base = 's3://stanford-pantheon/real-world/%s/' % node_desc
        s3_reports = s3_base + 'reports/'
        s3_job_logs = s3_base + 'job-logs/'

        url = 'https://s3.amazonaws.com/stanford-pantheon/real-world/%s/'
        s3_key_base = url % node_desc
        s3_key_reports = s3_key_base + 'reports/'

        reports_to_upload = [
            'pantheon_report.pdf', 'pantheon_summary.png',
            'pantheon_summary_mean.png', 'pantheon_summary_power.png']

        for sender in ['local', 'remote']:
            to_node = True if sender == 'local' else False
            payload = {
                'node': self.measurement_node,
                'link': self.link,
                'to_node': to_node,
                'time': d[sender]['time'],
            }

            # upload data logs
            data_logs = path.basename(d[sender]['tar'])

            cmd = 'aws s3 cp %s %s' % (
                d[sender]['tar'], path.join(s3_base, data_logs))
            check_call(self.ssh_cmd + [cmd])

            payload['data'] = path.join(s3_key_base, data_logs)

            # upload reports and job logs
            for report in reports_to_upload:
                src_path = path.join(d[sender]['data_dir'], report)

                dst_file = '%s-%s' % (
                    d[sender]['title'], report.replace('_', '-'))
                dst_url = path.join(s3_reports, dst_file)

                cmd = 'aws s3 cp %s %s' % (src_path, dst_url)
                check_call(self.ssh_cmd + [cmd])

                # add s3 file to payload of POST request
                s3_key_file = path.join(s3_key_reports, dst_file)
                if 'pantheon-summary.png' in s3_key_file:
                    payload['summary'] = s3_key_file
                elif 'pantheon-summary-mean.png' in s3_key_file:
                    payload['summary_mean'] = s3_key_file
                elif 'pantheon-report.pdf' in s3_key_file:
                    payload['report'] = s3_key_file

            job_log = path.basename(d[sender]['job_log'])
            cmd = 'aws s3 cp %s %s' % (
                d[sender]['job_log'], path.join(s3_job_logs, job_log))
            check_call(self.ssh_cmd + [cmd])

            # post update to website
            self.post_to_website(payload)

        # remove data directories and tar
        cmd = 'rm -rf %s /tmp/pantheon-tmp' % self.pdata
        check_call(self.ssh_cmd + [cmd])


    def run(self):
        # run bidirectional experiments
        d = self.test()

        # generate graphs and report
        self.analyze(d)

        # upload results to S3
        self.upload(d)


def main():
    config = parse_config()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cloud_server', choices=config['cloud_servers'].keys())
    parser.add_argument(
        'measurement_node', choices=config['measurement_nodes'].keys())
    parser.add_argument(
        '--run-times', metavar='TIMES', type=int, default=1,
        help='run times of each scheme (default 1)')
    parser.add_argument('--ppp0', action='store_true',
                        help='use ppp0 interface on node')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='run all schemes')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='run a space-separated list of schemes')
    args = parser.parse_args()

    Console(args, config).run()


if __name__ == '__main__':
    main()
