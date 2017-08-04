#!/usr/bin/env python

import os
from os import path
import argparse
import requests
from helpers.helpers import parse_config, check_call, utc_date


class Console(object):
    def __init__(self, args, config):
        # common args
        self.expt_type = args.expt_type
        self.flows = args.flows
        self.run_times = args.run_times

        if args.all:
            self.schemes = '--all'
        elif args.schemes is not None:
            self.schemes = '--schemes "%s"' % args.schemes

        # special args for each expt_type
        if args.expt_type == 'node':
            self.master_name = args.cloud
            self.slave_name = args.node
            self.master = config['aws_servers'][args.cloud]
            self.slave = config['nodes'][args.node]
            self.ppp0 = args.ppp0
        elif args.expt_type == 'cloud':
            self.master_name = args.cloud_master
            self.slave_name = args.cloud_slave
            self.master = config['gce_servers'][args.cloud_master]
            self.slave = config['gce_servers'][args.cloud_slave]
            self.ppp0 = False

        self.master_host = self.master['user'] + '@' + self.master['addr']
        self.slave_host = self.slave['user'] + '@' + self.slave['addr']

        # default args
        self.runtime = 30  # s

    def test(self):
        # create data dir
        self.data_dir = '~/pantheon_data'
        check_call(['ssh', self.master_host, 'mkdir -p ' + self.data_dir])

        cmd = (
            '~/pantheon/test/test.py remote {s.slave_host}:~/pantheon '
            '{s.schemes} -t {s.runtime} --run-times {s.run_times} '
            '--tunnel-server local --local-addr {s.master[addr]} '
            '--local-desc "{s.master[desc]}" --remote-desc "{s.slave[desc]}" '
            '--random-order --pkill-cleanup').format(s=self)

        title_template = '%s to %s'

        # NTP
        if 'ntp' in self.master:
            cmd += ' --ntp-addr ' + self.master['ntp']

        # runs
        if self.run_times > 1:
            title_template += ' %d runs' % self.run_times
        else:
            title_template += ' 1 run'

        # flows
        if self.flows > 1:
            cmd += ' -f %d --interval %d' % (
                self.flows, self.runtime / self.flows)
            title_template += ' %d flows' % self.flows

        # cellular link
        slave_desc = self.slave['desc']
        if self.ppp0:
            cmd += ' --remote-if ppp0'
            slave_desc += ' ppp0'

        # run experiments
        d = {}

        for sender in ['local', 'remote']:
            d[sender] = {}

            if sender == 'local':
                title = title_template % (self.master['desc'], slave_desc)
            else:
                title = title_template % (slave_desc, self.master['desc'])

            title = title.replace(' ', '-')

            d[sender]['time'] = utc_date()
            d[sender]['title'] = '%s-%s' % (d[sender]['time'], title)

            d[sender]['data_dir'] = path.join(
                self.data_dir, d[sender]['title'])
            d[sender]['job_log'] = path.join(
                self.data_dir, '%s.log' % d[sender]['title'])

            cmd_in_ssh = cmd + ' --sender %s --data-dir %s >> %s 2>&1' % (
                sender, d[sender]['data_dir'], d[sender]['job_log'])
            check_call(['ssh', self.master_host, cmd_in_ssh])

        return d

    def compress(self, d):
        # compress logs
        for sender in ['local', 'remote']:
            cmd = 'cd {data_dir} && tar -I pxz -cf {t}.tar.xz {t}'.format(
                data_dir=self.data_dir, t=d[sender]['title'])
            check_call(['ssh', self.master_host, cmd])

            d[sender]['tar'] = d[sender]['data_dir'] + '.tar.xz'

    def analyze(self, d):
        analyze_cmd = '~/pantheon/analysis/analyze.py --data-dir %s >> %s 2>&1'

        for sender in ['local', 'remote']:
            cmd = analyze_cmd % (
                d[sender]['data_dir'], d[sender]['job_log'])
            check_call(['ssh', self.master_host, cmd])

    def post_to_website(self, payload):
        update_url = os.environ['UPDATE_URL']
        url = 'http://pantheon.stanford.edu/%s/%s/' % (update_url,
                                                       self.expt_type)

        client = requests.session()
        response = client.get(url)

        csrftoken = client.cookies['csrftoken']
        payload['csrfmiddlewaretoken'] = csrftoken

        client.post(url, data=payload, headers=dict(Referer=url))

    def upload(self, d):
        slave_desc = self.slave['desc'].replace(' ', '-')

        s3_base = 's3://stanford-pantheon/real-world/%s/' % slave_desc
        s3_reports = s3_base + 'reports/'
        s3_job_logs = s3_base + 'job-logs/'

        s3_url_base = ('https://s3.amazonaws.com/stanford-pantheon/'
                       'real-world/%s/' % slave_desc)
        s3_url_reports = s3_url_base + 'reports/'

        reports_to_upload = ['pantheon_report.pdf', 'pantheon_summary.png',
                             'pantheon_summary_mean.png']

        for sender in ['local', 'remote']:
            to_node = True if sender == 'local' else False

            if self.expt_type == 'node':
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
                    'flow': self.flows,
                    'time': d[sender]['time'],
                }
            elif self.expt_type == 'cloud':
                payload = {
                    'src': self.master_name,
                    'dst': self.slave_name,
                    'flow': self.flows,
                    'time': d[sender]['time'],
                }

            # upload data logs
            data_logs = path.basename(d[sender]['tar'])

            cmd = 'aws s3 cp %s %s' % (
                d[sender]['tar'], path.join(s3_base, data_logs))
            check_call(['ssh', self.master_host, cmd])

            payload['log'] = path.join(s3_url_base, data_logs)

            # upload reports and job logs
            for report in reports_to_upload:
                src_path = path.join(d[sender]['data_dir'], report)

                dst_file = '%s-%s' % (
                    d[sender]['title'], report.replace('_', '-'))
                dst_url = path.join(s3_reports, dst_file)

                cmd = 'aws s3 cp %s %s' % (src_path, dst_url)
                check_call(['ssh', self.master_host, cmd])

                # add s3 file to payload of POST request
                s3_url_file = path.join(s3_url_reports, dst_file)

                if report == 'pantheon_report.pdf':
                    payload['report'] = s3_url_file
                elif report == 'pantheon_summary.png':
                    payload['graph1'] = s3_url_file
                elif report == 'pantheon_summary_mean.png':
                    payload['graph2'] = s3_url_file

            job_log = path.basename(d[sender]['job_log'])
            cmd = 'aws s3 cp %s %s' % (
                d[sender]['job_log'], path.join(s3_job_logs, job_log))
            check_call(['ssh', self.master_host, cmd])

            # post update to website
            self.post_to_website(payload)

        # remove data directories and tar
        cmd = 'rm -rf %s /tmp/pantheon-tmp' % self.data_dir
        check_call(['ssh', self.master_host, cmd])


    def run(self):
        # run bidirectional experiments
        d = self.test()

        # compress logs
        self.compress(d)

        # generate graphs and report
        self.analyze(d)

        # upload results to S3
        self.upload(d)


def main():
    config = parse_config()
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='expt_type')

    node_parser = subparsers.add_parser(
        'node', help='between a measurement node and the closest cloud server')
    cloud_parser = subparsers.add_parser(
        'cloud', help='between two cloud servers')

    node_parser.add_argument('cloud', help='AWS cloud server',
                             choices=config['aws_servers'].keys())
    node_parser.add_argument('node', help='measurement node',
                             choices=config['nodes'].keys())
    node_parser.add_argument(
        '--ppp0', action='store_true', help='use ppp0 interface on node')

    cloud_parser.add_argument('cloud_master', help='GCE cloud server',
                              choices=config['gce_servers'].keys())
    cloud_parser.add_argument('cloud_slave', help='GCE cloud server',
                              choices=config['gce_servers'].keys())

    for subparser in [node_parser, cloud_parser]:
        subparser.add_argument(
            '-f', '--flows', metavar='FLOWS', type=int, default=1,
            help='number of flows (default 1)')
        subparser.add_argument(
            '--run-times', metavar='TIMES', type=int, default=1,
            help='run times of each scheme (default 1)')

        group = subparser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--all', action='store_true', help='run all schemes')
        group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                           help='run a space-separated list of schemes')
    args = parser.parse_args()

    Console(args, config).run()


if __name__ == '__main__':
    main()
