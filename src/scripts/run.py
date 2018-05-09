#!/usr/bin/env python

import os
from os import path
import sys
import argparse
from multiprocessing import Process

import context
from helpers import utils, round_robin_tournament
from helpers.subprocess_wrappers import Popen, PIPE


def start_hosts(expt_type):
    sys.stderr.write('----- Starting hosts -----\n')

    # set of live hosts (including nodes and cloud servers)
    live_hosts = set()

    # list of cloud server to start
    clouds_to_start = []

    if expt_type == 'node_to_cloud':
        host_status = utils.check_ssh_connection(
                utils.host_cfg['nodes'].keys())

        for host, status in host_status.iteritems():
            if status:
                live_hosts.add(host)

                # get peer cloud of host
                node_cfg = utils.host_cfg['nodes'][host]
                peer_cloud = node_cfg['peer_cloud']
                clouds_to_start.append(peer_cloud)

        # run aws.py
        aws_py = path.join(context.scripts_dir, 'aws.py')
        with open(os.devnull, 'w') as DEVNULL:
            Popen([aws_py, 'start', '--hosts', ' '.join(clouds_to_start)],
                   stdout=DEVNULL, stderr=DEVNULL).wait()

    else:
        if expt_type == 'cloud_to_cloud':
            gce_server_type = 'gce_servers'
        elif expt_type == 'emulation':
            gce_server_type = 'emu_servers'

        for host in utils.host_cfg[gce_server_type]:
            clouds_to_start.append(host)

        # run gce.py
        gce_py = path.join(context.scripts_dir, 'gce.py')
        with open(os.devnull, 'w') as DEVNULL:
            Popen([gce_py, 'start', gce_server_type],
                   stdout=DEVNULL, stderr=DEVNULL).wait()

    # check SSH connections to cloud servers
    host_status = utils.check_ssh_connection(
            clouds_to_start, retry_times=2, retry_timeout=20)

    for host, status in host_status.iteritems():
        if not status:
            sys.exit('Failed to start %s' % host)

        live_hosts.add(host)

    # print live hosts
    sys.stderr.write('Live hosts:')
    for host in live_hosts:
        sys.stderr.write(' ' + host)
    sys.stderr.write('\n')

    return live_hosts


def setup_cellular_links(nodes_with_cellular):
    sys.stderr.write('Setting up cellular links...\n')

    live_cellular_nodes = set()

    # run pppd commands
    utils.run_pppd(nodes_with_cellular)

    # set up ppp0 interface
    utils.setup_ppp0_interface(nodes_with_cellular)

    # check ppp0 connections
    host_status = utils.check_ppp0_connection(
            nodes_with_cellular, retry_times=2, retry_timeout=10)
    for host, status in host_status.iteritems():
        if status:
            live_cellular_nodes.add(host)

    # print live cellular hosts
    sys.stderr.write('Live hosts with working cellular links:')
    for host in live_cellular_nodes:
        sys.stderr.write(' ' + host)
    sys.stderr.write('\n')

    return live_cellular_nodes


def setup(expt_type, hosts):
    sys.stderr.write('----- Setting up hosts -----\n')

    # cleanup
    utils.cleanup(hosts)

    # update repository
    utils.update_repository(hosts)

    # setup system
    utils.setup_system(hosts)

    # setup after reboot
    utils.setup_after_reboot(hosts)


def analyze():
    sys.stderr.write('----- Performing analysis -----\n')


def upload_to_s3():
    sys.stderr.write('----- Uploading logs to Amazon S3 -----\n')


def post_to_website():
    sys.stderr.write('----- Posting results to Pantheon website -----\n')


def master_slave_expand(master, slave, cmd_tmpl):
    # split cmd_tmpl
    cmd_splitted = cmd_tmpl.split()

    master_cfg = utils.get_host_cfg(master)
    slave_cfg = utils.get_host_cfg(slave)

    # start preparing experiment's title
    expt_time = utils.utc_date()
    title = expt_time

    # refine descriptions
    master_desc = master_cfg['desc']
    slave_desc = slave_cfg['desc']
    if 'ppp0' in cmd_splitted: # cellular experiment
        slave_desc += ' ppp0'

    if '--sender' not in cmd_splitted:
        sys.exit('Specify --sender explicitly')

    sender_idx = cmd_splitted.index('--sender')
    sender = cmd_splitted[sender_idx + 1]

    # master to slave
    if sender == 'local':
        title += ' %s to %s' % (master_desc, slave_desc)
    # slave to master
    elif sender == 'remote':
        title += ' %s to %s' % (slave_desc, master_desc)

    # add runs to the title (if runs > 1)
    if '--run-times' in cmd_splitted:
        runs_idx = cmd_splitted.index('--run-times')
        runs = int(cmd_splitted[runs_idx + 1])

        if runs > 1:
            title += ' %d runs' % runs

    # add flows to the title (if not single flow)
    if '-f' in cmd_splitted:
        flow_idx = cmd_splitted.index('-f')
        flows = int(cmd_splitted[flow_idx + 1])

        if flows > 1:
            title += ' %d flows' % flows

    # finish preparing experiment's title
    title = title.replace(' ', '-')

    # generate a dictionary of keys for formatting cmd_tmpl
    cmd_dict = {
        'slave_addr': utils.get_host_addr(slave),
        'master_ip': master_cfg['ip'],
        'master_desc': master_cfg['desc'],
        'slave_desc': slave_desc,
        'ntp_addr': slave_cfg['ntp'],
    }

    data_dir = utils.meta['data_dir']
    cmd_dict['data_dir'] = path.join(data_dir, title)
    cmd_dict['job_log'] = path.join(data_dir, '%s.log' % title)

    # store extra useful information
    cmd_dict['title'] = title

    return cmd_dict


# smallest unit of real-world experiment that will be run in parallel
def run_real_world_experiment(master, slave, cmd_tmpl):
    # 4. fill in the remaining varialbes
    cmd_dict = master_slave_expand(master, slave, cmd_tmpl)
    final_cmd = utils.safe_format(cmd_tmpl, cmd_dict)
    print(final_cmd)


def run_node_to_cloud(cellular_nodes, ethernet_nodes):
    sys.stderr.write('----- Running node-to-cloud experiments -----\n')

    # convert lists to sets for faster lookup
    cellular_nodes = set(cellular_nodes)
    ethernet_nodes = set(ethernet_nodes)

    cfg = utils.expt_cfg['real_world']
    matrix = utils.expand_matrix(cfg['matrix'])

    # run each cellular/ethernet experiment on all node-cloud pairs in parallel
    for mat_dict in matrix:
        for job in cfg['jobs']:
            cmd_tmpl = job['command']
            # 1. expand macros
            cmd_tmpl = utils.safe_format(cmd_tmpl, cfg['macros'])
            # 2. expand variables in mat_dict
            cmd_tmpl = utils.safe_format(cmd_tmpl, mat_dict)
            # 3. expand meta
            cmd_tmpl = utils.safe_format(cmd_tmpl, utils.meta)

            # create a process
            procs = []
            for node, node_cfg in utils.host_cfg['nodes'].iteritems():
                if '--remote-if ppp0' in cmd_tmpl:
                    if node not in cellular_nodes:
                        continue
                else:
                    if node not in ethernet_nodes:
                        continue

                peer_cloud = node_cfg['peer_cloud']

                p = Process(target=run_real_world_experiment,
                            args=(peer_cloud, node, cmd_tmpl))
                p.start()
                procs.append(p)

            for p in procs:
                p.join()


def run_cloud_to_cloud(hosts):
    sys.stderr.write('----- Running cloud-to-cloud experiments -----\n')

    # create a schedule for a "round-robin tournament" among live cloud servers
    schedule = round_robin_tournament.schedule(hosts)

    cfg = utils.expt_cfg['real_world']
    matrix = utils.expand_matrix(cfg['matrix'])

    # run each ethernet experiment on every pair of cloud servers in parallel
    for schedule_round in schedule:
        for mat_dict in matrix:
            for job in cfg['jobs']:
                cmd_tmpl = job['command']
                # 1. expand macros
                cmd_tmpl = utils.safe_format(cmd_tmpl, cfg['macros'])
                # 2. expand variables in mat_dict
                cmd_tmpl = utils.safe_format(cmd_tmpl, mat_dict)
                # 3. expand meta
                cmd_tmpl = utils.safe_format(cmd_tmpl, utils.meta)

                # create a process
                procs = []
                for pair in schedule_round:
                    p = Process(target=run_real_world_experiment,
                                args=(pair[0], pair[1], cmd_tmpl))
                    p.start()
                    procs.append(p)

                for p in procs:
                    p.join()


def run_emulation(hosts):
    pass


def main():
    # get commands to run from experiments.yml
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'expt_type', choices=['node_to_cloud', 'cloud_to_cloud', 'emulation'])
    args = parser.parse_args()

    expt_type = args.expt_type

    # start servers
    live_hosts = start_hosts(expt_type)

    # run setup
    setup(expt_type, live_hosts)

    if expt_type == 'node_to_cloud':
        live_ethernet_nodes = []
        nodes_with_cellular = []

        for node, node_cfg in utils.host_cfg['nodes'].iteritems():
            if node in live_hosts:
                live_ethernet_nodes.append(node)

                if node_cfg['cellular']:
                    nodes_with_cellular.append(node)

        live_cellular_nodes = setup_cellular_links(nodes_with_cellular)

        run_node_to_cloud(live_cellular_nodes, live_ethernet_nodes)

    elif expt_type == 'cloud_to_cloud':
        run_cloud_to_cloud(live_hosts)

    elif expt_type == 'emulation':
        run_emulation(live_hosts)


if __name__ == '__main__':
    main()
