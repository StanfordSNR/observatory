#!/usr/bin/env python

import os
from os import path
import sys
import json
import pickle
import argparse
import requests
import errno
from helpers.helpers import parse_config, check_call, utc_date


class Console(object):
    def __init__(self, args, config):
        # common args
        self.expt_type = args.expt_type
        self.flows = args.flows
        self.run_times = args.run_times
        self.runtime = 30  # s

        if args.all:
            self.schemes = '--all'
        elif args.schemes is not None:
            self.schemes = '--schemes "%s"' % args.schemes

        # special args for each expt_type
        if args.expt_type == 'emu':
            self.desc = args.desc
            self.id = args.id

            self.uplink_trace = args.uplink_trace
            self.downlink_trace = args.downlink_trace
            self.prepend_mm_cmds = args.prepend_mm_cmds
            self.append_mm_cmds = args.append_mm_cmds
            self.extra_mm_link_args = args.extra_mm_link_args

            self.master_name = args.server
            for server_type in config:
                if args.server in config[server_type]:
                    self.master = config[server_type][args.server]
        else:
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

            self.slave_host = self.slave['user'] + '@' + self.slave['addr']

        self.master_host = self.master['user'] + '@' + self.master['addr']

        # create data dir
        self.data_dir = '~/pantheon_data'
        check_call(['ssh', self.master_host, 'mkdir -p ' + self.data_dir])

    def emu_test(self):
        cmd = (
            '~/pantheon/test/test.py local {s.schemes} -t {s.runtime} '
            '--run-times {s.run_times} --random-order '
            '--pkill-cleanup').format(s=self)
        self.mm_cmd = ''

        if self.prepend_mm_cmds:
            cmd += ' --prepend-mm-cmds "%s"' % self.prepend_mm_cmds
            self.mm_cmd += self.prepend_mm_cmds + ' '

        if self.uplink_trace:
            cmd += ' --uplink-trace ' + self.uplink_trace
            uplink_trace = path.basename(self.uplink_trace)
        else:
            uplink_trace = '12mbps.trace'

        if self.downlink_trace:
            cmd += ' --downlink-trace ' + self.downlink_trace
            downlink_trace = path.basename(self.downlink_trace)
        else:
            downlink_trace = '12mbps.trace'

        self.mm_cmd += 'mm-link %s %s ' % (uplink_trace, downlink_trace)

        if self.extra_mm_link_args:
            cmd += ' --extra-mm-link-args "%s"' % self.extra_mm_link_args
            self.mm_cmd += self.extra_mm_link_args + ' '

        if self.append_mm_cmds:
            cmd += ' --append-mm-cmds "%s"' % self.append_mm_cmds
            self.mm_cmd += self.append_mm_cmds + ' '

        self.mm_cmd = self.mm_cmd.strip()

        title = 'emu ' + self.id

        # runs
        if self.run_times > 1:
            title += ' %d runs' % self.run_times
        else:
            title += ' 1 run'

        # flows
        if self.flows > 1:
            cmd += ' -f %d --interval %d' % (
                self.flows, self.runtime / self.flows)
            title += ' %d flows' % self.flows

        title = title.replace(' ', '-')

        d = {'sender': {}}

        for sender in d:
            d[sender]['time'] = utc_date()
            d[sender]['title'] = '%s-%s' % (d[sender]['time'], title)

            d[sender]['data_dir'] = path.join(
                self.data_dir, d[sender]['title'])
            d[sender]['job_log'] = path.join(
                self.data_dir, '%s.log' % d[sender]['title'])

            cmd_in_ssh = cmd + ' --data-dir %s >> %s 2>&1' % (
                d[sender]['data_dir'], d[sender]['job_log'])
            check_call(['ssh', self.master_host, cmd_in_ssh])

        return d


    def real_test(self):
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
        d = {'local': {}, 'remote': {}}

        for sender in d:
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
        for sender in d:
            cmd = 'cd {data_dir} && tar czvf {t}.tar.gz {t}'.format(
                data_dir=self.data_dir, t=d[sender]['title'])
            check_call(['ssh', self.master_host, cmd])

            d[sender]['tar'] = d[sender]['data_dir'] + '.tar.gz'

    def analyze(self, d):
        analyze_cmd = '~/pantheon/analysis/analyze.py --data-dir %s >> %s 2>&1'

        for sender in d:
            cmd = analyze_cmd % (
                d[sender]['data_dir'], d[sender]['job_log'])
            check_call(['ssh', self.master_host, cmd])

            # load the pkl file to add to payload
            pkl_src = path.join(d[sender]['data_dir'], 'perf_data.pkl')
            pkl_src = '%s:%s' % (self.master_host, pkl_src)
            pkl_dest = '/tmp/pantheon-tmp/'
            pkl_path = path.join(pkl_dest, 'perf_data.pkl')

            try:
                os.makedirs(pkl_dest)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

            check_call(['scp', pkl_src, pkl_path])
            with open(pkl_path) as pkl_file:
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
                elif report == 'pantheon_summary.svg':
                    payload['graph1'] = s3_url_file
                elif report == 'pantheon_summary_mean.svg':
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
        if self.expt_type == 'emu':
            d = self.emu_test()
        else:
            d = self.real_test()

        # compress logs
        self.compress(d)

        # generate stats, graphs and report
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
    emu_parser = subparsers.add_parser('emu', help='in emulation')

    # node
    node_parser.add_argument('cloud', help='AWS cloud server',
                             choices=config['aws_servers'].keys())
    node_parser.add_argument('node', help='measurement node',
                             choices=config['nodes'].keys())
    node_parser.add_argument(
        '--ppp0', action='store_true', help='use ppp0 interface on node')

    # cloud
    cloud_parser.add_argument('cloud_master', help='GCE cloud server',
                              choices=config['gce_servers'].keys())
    cloud_parser.add_argument('cloud_slave', help='GCE cloud server',
                              choices=config['gce_servers'].keys())

    # emu
    emu_parser.add_argument('server', help='server to run emulation on')
    emu_parser.add_argument('--desc', help='description of emulation')
    emu_parser.add_argument('--id', help='a distinguished ID used in filename')
    emu_parser.add_argument('--uplink-trace')
    emu_parser.add_argument('--downlink-trace')
    emu_parser.add_argument('--prepend-mm-cmds')
    emu_parser.add_argument('--append-mm-cmds')
    emu_parser.add_argument('--extra-mm-link-args')

    for subparser in [node_parser, cloud_parser, emu_parser]:
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
