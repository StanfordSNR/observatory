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

    def run(self):
        # run bidirectional experiments
        if self.expt_type == 'emu':
            d = self.emu_test()
        else:
            d = self.real_test()

        self.d = d


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

    console = Console(args, config)
    console.run()

    if args.expt_type == 'node':
        node = args.node
        if args.ppp0:
            node += '_ppp0'
        saved_pkl_name = '%s_%s_%sflows_%sruns_%s.pkl' % (
            node, args.cloud, args.flows, args.run_times, utc_date())
    elif args.expt_type == 'cloud':
        saved_pkl_name = '%s_%s_%sflows_%sruns_%s.pkl' % (
            args.cloud_master, args.cloud_slave, args.flows, args.run_times, utc_date())

    with open(saved_pkl_name, 'wb') as saved_console:
        pickle.dump(console, saved_console)


if __name__ == '__main__':
    main()
