#!/usr/bin/env python

from os import path
import argparse
from helpers.helpers import parse_config, check_call, Popen, utc_date


class Console(object):
    def __init__(self, args, config):
        self.server = config['cloud_servers'][args.cloud_server]
        self.node = config['measurement_nodes'][args.measurement_node]

        self.server_host = '%s@%s' % (self.server['user'], self.server['addr'])
        self.node_host = '%s@%s' % (self.node['user'], self.node['addr'])
        self.ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                        self.server_host]

        self.run_times = args.run_times

        if args.all:
            self.schemes = '--all'
        elif args.schemes is not None:
            self.schemes = '--schemes "%s"' % args.schemes

    def test(self):
        common_cmd = (
            '~/pantheon/test/test.py remote {s.node_host}:~/pantheon '
            '{s.schemes} --random-order --run-times {s.run_times} '
            '--tunnel-server local --local-addr {s.server[addr]} '
            '--local-desc "{s.server[desc]}" --remote-desc "{s.node[desc]}" '
            '--ntp-addr {s.server[ntp]} --pkill-cleanup').format(s=self)

        runs_str = 'runs' if self.run_times > 1 else 'run'
        expt_title = '%s to %s' + ' %d %s' % (self.run_times, runs_str)

        d = {}
        procs = []
        for sender in ['local', 'remote']:
            d[sender] = {}
            if sender == 'local':
                title = expt_title % (
                    self.server['desc'], self.node['desc'])
            else:
                title = expt_title % (
                    self.node['desc'], self.server['desc'])

            title = title.replace(' ', '-')
            d[sender]['title'] = '%s-%s' % (utc_date(), title)
            d[sender]['data_dir'] = '/tmp/%s' % d[sender]['title']
            d[sender]['job_log'] = '/tmp/%s.log' % d[sender]['title']

            # run experiments
            cmd = common_cmd + ' --sender %s --data-dir %s >> %s 2>&1' % (
                sender, d[sender]['data_dir'], d[sender]['job_log'])
            check_call(self.ssh_cmd + [cmd])

            # compress logs
            cmd = 'cd /tmp && tar cJf %s %s' % (
                d[sender]['title'] + '.tar.xz', d[sender]['title'])
            procs.append(Popen(self.ssh_cmd + [cmd]))

            d[sender]['tar'] = d[sender]['data_dir'] + '.tar.xz'

        for proc in procs:
            proc.wait()

        self.d = d

    def analyze(self):
        d = self.d
        analyze_cmd = '~/pantheon/analysis/analyze.py --data-dir %s >> %s 2>&1'

        procs = []
        for sender in ['local', 'remote']:
            cmd = analyze_cmd % (
                d[sender]['data_dir'], d[sender]['job_log'])
            procs.append(Popen(self.ssh_cmd + [cmd]))

        for proc in procs:
            proc.wait()

    def upload(self):
        d = self.d
        node_desc = self.node['desc'].replace(' ', '-')
        s3_base = 's3://stanford-pantheon/real-world/%s' % node_desc
        s3_reports = s3_base + '/reports'
        s3_job_logs = s3_base + '/job-logs'
        reports_to_upload = [
            'pantheon_report.pdf', 'pantheon_summary.png',
            'pantheon_summary_mean.png', 'pantheon_summary_power.png']

        # upload data
        procs = []
        for sender in ['local', 'remote']:
            cmd = 'aws s3 cp %s %s/%s' % (
                d[sender]['tar'], s3_base, path.basename(d[sender]['tar']))
            procs.append(Popen(self.ssh_cmd + [cmd]))

        for proc in procs:
            proc.wait()

        # upload reports and job logs
        for sender in ['local', 'remote']:
            for report in reports_to_upload:
                src_path = '%s/%s' % (d[sender]['data_dir'], report)
                dst_path = '%s/%s-%s' % (
                    s3_reports, d[sender]['title'], report.replace('_', '-'))
                cmd = 'aws s3 cp %s %s' % (src_path, dst_path)
                check_call(self.ssh_cmd + [cmd])

            cmd = 'aws s3 cp %s %s/%s' % (
                d[sender]['job_log'], s3_job_logs,
                path.basename(d[sender]['job_log']))
            check_call(self.ssh_cmd + [cmd])


        # remove data directories and tar
        for sender in ['local', 'remote']:
            cmd = 'rm -rf %s %s %s /tmp/pantheon-tmp' % (
                d[sender]['data_dir'], d[sender]['tar'], d[sender]['job_log'])
            check_call(self.ssh_cmd + [cmd])


    def run(self):
        # run bidirectional experiments
        self.test()

        # generate graphs and report
        self.analyze()

        # upload results to S3
        self.upload()


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

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all', action='store_true',
        help='set up all schemes specified in src/vantage_points.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='set up a space-separated list of schemes')
    args = parser.parse_args()

    Console(args, config).run()


if __name__ == '__main__':
    main()
