#!/usr/bin/env python

import os
from os import path
import sys
import time
import argparse
import requests
import json
import shlex
from multiprocessing import Process
from collections import deque

import context
from helpers import utils, round_robin_tournament
from helpers.subprocess_wrappers import Popen, PIPE, check_call, check_output


expt_type = None
no_post_log = None


def start_hosts():
    sys.stderr.write('----- Starting hosts -----\n')

    # set of live hosts (including nodes and cloud servers)
    live_hosts = set()

    # list of cloud server to start
    clouds_to_start = []

    if expt_type == 'node':
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
        if expt_type == 'cloud':
            gce_server_type = 'gce_servers'
        elif expt_type == 'emu':
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
    if not live_hosts:
        sys.stderr.write(' None\n')
    else:
        for host in live_hosts:
            sys.stderr.write(' ' + host)
        sys.stderr.write('\n')

    return live_hosts


def stop_hosts():
    if expt_type == 'node':
        # run aws.py
        aws_py = path.join(context.scripts_dir, 'aws.py')
        with open(os.devnull, 'w') as DEVNULL:
            Popen([aws_py, 'stop'], stdout=DEVNULL, stderr=DEVNULL).wait()

    else:
        if expt_type == 'cloud':
            gce_server_type = 'gce_servers'
        elif expt_type == 'emu':
            gce_server_type = 'emu_servers'

        # run gce.py
        gce_py = path.join(context.scripts_dir, 'gce.py')
        with open(os.devnull, 'w') as DEVNULL:
            Popen([gce_py, 'stop', gce_server_type],
                   stdout=DEVNULL, stderr=DEVNULL).wait()


def setup_cellular_links(nodes_with_cellular):
    sys.stderr.write('Setting up cellular links...\n')

    live_cellular_nodes = set()

    # run pppd commands
    utils.run_pppd(nodes_with_cellular)
    time.sleep(5)

    # set up cellular interfaces
    utils.setup_cellular_interface(nodes_with_cellular)

    # check if cellular connections are up
    host_status = utils.check_cellular_connection(
            nodes_with_cellular, retry_times=2, retry_timeout=10)
    for host, status in host_status.iteritems():
        if status:
            live_cellular_nodes.add(host)

    # print live cellular hosts
    sys.stderr.write('Live hosts with working cellular links:')
    if not live_cellular_nodes:
        sys.stderr.write(' None\n')
    else:
        for host in live_cellular_nodes:
            sys.stderr.write(' ' + host)
        sys.stderr.write('\n')

    return live_cellular_nodes


def setup(hosts):
    sys.stderr.write('----- Setting up hosts -----\n')

    # update repository
    utils.update_repository(hosts)

    # setup system
    utils.setup_system(hosts)

    # setup after reboot
    utils.setup_after_reboot(hosts)


def get_param_from_cmd(cmd_splitted, key):
    if key in cmd_splitted:
        idx = cmd_splitted.index(key)
        if idx + 1 < len(cmd_splitted):
            return cmd_splitted[idx + 1]
        else:
            return None
    else:
        return None


def compress(d):
    # compress raw packet logs
    cmd = 'cd {data_base_dir} && tar czvf {title}.tar.gz {title}'.format(
            data_base_dir=utils.meta['data_base_dir'], title=d['title'])
    check_call(['ssh', d['master_addr'], cmd])

    d['tar'] = path.join(utils.meta['data_base_dir'], '%s.tar.gz' % d['title'])

    # compress raw ingress/egress logs
    title_uid = d['title'] + '-UID'
    cmd = ('cd {tmp_dir} && mkdir {title_uid} && '
           'mv *.log.ingress *.log.egress {title_uid} && '
           'tar czvf {title_uid}.tar.gz {title_uid}'.format(
            tmp_dir=utils.meta['tmp_dir'], title_uid=title_uid))
    check_call(['ssh', d['master_addr'], cmd])

    d['tar_uid'] = path.join(utils.meta['tmp_dir'], '%s.tar.gz' % title_uid)


def analyze(d):
    sys.stderr.write('----- Performing analysis -----\n')
    cmd = '{analyze_path} --data-dir {data_dir} >> {job_log} 2>&1'.format(
            analyze_path=utils.meta['analyze_path'],
            data_dir=d['data_dir'], job_log=d['job_log'])
    check_call(['ssh', d['master_addr'], cmd])


def upload(d):
    # upload to S3
    sys.stderr.write('----- Uploading logs to Amazon S3 -----\n')

    if expt_type == 'emu':
        s3_folder = 'stanford-pantheon/emulation/'
    else:
        slave_desc = d['slave_desc'].replace(' ', '-')
        s3_folder = 'stanford-pantheon/real-world/%s/' % slave_desc
    d['s3_folder'] = s3_folder

    s3_base = 's3://' + s3_folder

    # upload reports
    s3_reports = path.join(s3_base, 'reports')
    reports_to_upload = ['pantheon_perf.json',
                         'pantheon_report.pdf',
                         'pantheon_summary.svg',
                         'pantheon_summary_mean.svg']
    for report in reports_to_upload:
        report_path = path.join(d['data_dir'], report)

        dst_file = '%s-%s' % (d['title'], report.replace('_', '-'))
        d[report] = dst_file
        dst_url = path.join(s3_reports, dst_file)

        cmd = 'aws s3 cp %s %s' % (report_path, dst_url)
        check_call(['ssh', d['master_addr'], cmd])

    # upload job logs
    s3_job_logs = path.join(s3_base, 'job-logs')
    cmd = 'aws s3 cp %s %s' % (
        d['job_log'], path.join(s3_job_logs, path.basename(d['job_log'])))
    check_call(['ssh', d['master_addr'], cmd])

    # upload data logs
    cmd = 'aws s3 cp %s %s' % (
        d['tar'], path.join(s3_base, path.basename(d['tar'])))
    check_call(['ssh', d['master_addr'], cmd])

    # upload ingress egress logs
    s3_uid_logs = path.join(s3_base, 'uid-logs')
    cmd = 'aws s3 cp %s %s' % (
        d['tar_uid'], path.join(s3_uid_logs, path.basename(d['tar_uid'])))
    check_call(['ssh', d['master_addr'], cmd])


def post_to_website(d):
    s3_url_base = 'https://s3.amazonaws.com/' + d['s3_folder']
    s3_url_reports = path.join(s3_url_base, 'reports')

    update_url = 'https://pantheon.stanford.edu/%s/%s/' % (
            os.environ['PANTHEON_UPDATE_URL'], expt_type)

    # GET CSRF token
    client = requests.session()
    response = client.get(update_url)
    csrftoken = client.cookies['csrftoken']

    payload = {}
    payload['csrfmiddlewaretoken'] = csrftoken
    payload['time_created'] = d['expt_time']

    payload['logs'] = path.join(s3_url_base, path.basename(d['tar']))
    payload['uid_logs'] = path.join(s3_url_base, 'uid-logs',
                                    path.basename(d['tar_uid']))
    payload['report'] = path.join(s3_url_reports,
                                  d['pantheon_report.pdf'])
    payload['graph1'] = path.join(s3_url_reports,
                                  d['pantheon_summary.svg'])
    payload['graph2'] = path.join(s3_url_reports,
                                  d['pantheon_summary_mean.svg'])
    payload['perf_file'] = path.join(s3_url_reports,
                                  d['pantheon_perf.json'])

    payload['time'] = d['time']
    payload['runs'] = d['runs']
    payload['scenario'] = d['scenario']

    if expt_type == 'node':
        payload['node'] = d['node']
        payload['cloud'] = d['cloud']
        payload['to_node'] = d['to_node']
        payload['link'] = d['link']
    elif expt_type == 'cloud':
        payload['src'] = d['src']
        payload['dst'] = d['dst']
    elif expt_type == 'emu':
        payload['emu_scenario'] = d['emu_scenario']
        payload['emu_cmd'] = d['emu_cmd']
        payload['emu_desc'] = d['emu_desc']

    if not no_post_log:
        # post to pantheon website
        client.post(update_url, data=payload, headers=dict(Referer=update_url))
        sys.stderr.write('----- Posted results to Pantheon website -----\n')
    else:
        with open(no_post_log, 'a') as fh:
            json.dump(payload, fh)
            fh.write(os.linesep)


def master_slave_expand(master, slave, cmd_tmpl, expt_time):
    # split cmd_tmpl by spaces but preserve quoted substrings
    cmd_splitted = shlex.split(cmd_tmpl)

    master_cfg = utils.get_host_cfg(master)
    slave_cfg = utils.get_host_cfg(slave)

    # start preparing experiment's title
    title = expt_time

    # refine descriptions
    master_desc = master_cfg['desc']
    slave_desc = slave_cfg['desc']
    link = 'ethernet'

    if '{slave_cell_if}' in cmd_splitted and 'cell_if' in slave_cfg:
        slave_desc += ' cellular'
        link = 'cellular'

    sender = get_param_from_cmd(cmd_splitted, '--sender')
    if sender is None:
        sys.exit('Specify --sender explicitly')

    # master to slave
    if sender == 'local':
        title += ' %s to %s' % (master_desc, slave_desc)
    # slave to master
    elif sender == 'remote':
        title += ' %s to %s' % (slave_desc, master_desc)

    # add runs to the title (if runs > 1)
    runs = get_param_from_cmd(cmd_splitted, '--run-times')
    runs = int(runs) if runs is not None else 1
    if runs > 1:
        title += ' %d runs' % runs

    # add flows to the title (if not single flow)
    flows = get_param_from_cmd(cmd_splitted, '-f')
    flows = int(flows) if flows is not None else 1
    if flows > 1:
        title += ' %d flows' % flows

    # record time
    time = get_param_from_cmd(cmd_splitted, '-t')
    time = int(time) if time is not None else 30

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

    if 'eth_if' in master_cfg:
        cmd_dict['master_eth_if'] = master_cfg['eth_if']
    if 'eth_if' in slave_cfg:
        cmd_dict['slave_eth_if'] = slave_cfg['eth_if']
    if 'cell_if' in master_cfg:
        cmd_dict['master_cell_if'] = master_cfg['cell_if']
    if 'cell_if' in slave_cfg:
        cmd_dict['slave_cell_if'] = slave_cfg['cell_if']

    cmd_dict['data_dir'] = path.join(utils.meta['data_base_dir'], title)
    cmd_dict['job_log'] = path.join(utils.meta['tmp_dir'], '%s.log' % title)

    # store extra information to return
    cmd_dict['time'] = time
    cmd_dict['runs'] = runs

    if flows == 1:
        cmd_dict['scenario'] = '1_flow'
    elif flows == 3:
        cmd_dict['scenario'] = '3_flows'

    cmd_dict['sender'] = sender
    cmd_dict['link'] = link

    return cmd_dict


def create_mm_cmd(cmd_splitted):
    mm_cmd = ''

    prepend_cmd = get_param_from_cmd(cmd_splitted, '--prepend-mm-cmds')
    if prepend_cmd is not None:
        mm_cmd += prepend_cmd + ' '

    uptrace = get_param_from_cmd(cmd_splitted, '--uplink-trace')
    if uptrace is not None:
        uptrace = path.basename(uptrace)
    else:
        uptrace = '12mbps.trace'

    downtrace = get_param_from_cmd(cmd_splitted, '--downlink-trace')
    if downtrace is not None:
        downtrace = path.basename(downtrace)
    else:
        downtrace = '12mbps.trace'

    mm_cmd += 'mm-link %s %s ' % (uptrace, downtrace)

    mm_link_args = get_param_from_cmd(cmd_splitted, '--extra-mm-link-args')
    if mm_link_args is not None:
        mm_cmd += mm_link_args + ' '

    append_cmd = get_param_from_cmd(cmd_splitted, '--append-mm-cmds')
    if append_cmd is not None:
        mm_cmd += append_cmd + ' '

    mm_cmd = mm_cmd.strip()

    return mm_cmd


def emu_server_expand(emu_server, cmd_tmpl, job_cfg, expt_time):
    # split cmd_tmpl by spaces but preserve quoted substrings
    cmd_splitted = shlex.split(cmd_tmpl)

    # record runs
    runs = get_param_from_cmd(cmd_splitted, '--run-times')
    runs = int(runs) if runs is not None else 1

    # record flows
    flows = get_param_from_cmd(cmd_splitted, '-f')
    flows = int(flows) if flows is not None else 1

    # record time
    time = get_param_from_cmd(cmd_splitted, '-t')
    time = int(time) if time is not None else 30

    # prepare title
    title = expt_time + ' emu ' + str(job_cfg['scenario']);
    title = title.replace(' ', '-')

    # generate a dictionary of keys for formatting cmd_tmpl
    cmd_dict = {}

    cmd_dict['data_dir'] = path.join(utils.meta['data_base_dir'], title)
    cmd_dict['job_log'] = path.join(utils.meta['tmp_dir'], '%s.log' % title)

    # store extra information to return
    cmd_dict['time'] = time
    cmd_dict['runs'] = runs

    if flows == 1:
        cmd_dict['scenario'] = '1_flow'
    elif flows == 3:
        cmd_dict['scenario'] = '3_flows'

    # create a user-friendly mahimahi command to present
    cmd_dict['mm_cmd'] = create_mm_cmd(cmd_splitted)

    return cmd_dict


def analyze_and_upload(d):
    # compress results
    compress(d)

    # analyze results
    analyze(d)

    # upload logs to S3 and website
    upload(d)
    post_to_website(d)


# smallest unit of real-world experiment that will be run in parallel
def run_real_world_experiment(master, slave, cmd_tmpl):
    # cleanup
    utils.cleanup([master, slave])

    # 4. fill in the remaining varialbes
    expt_time = utils.utc_date()
    cmd_dict = master_slave_expand(master, slave, cmd_tmpl, expt_time)
    cmd = utils.safe_format(cmd_tmpl, cmd_dict)

    master_addr = utils.get_host_addr(master)
    final_cmd = ['ssh', master_addr, cmd]
    check_call(final_cmd)

    # prepare parameters used in analyze_and_upload
    d = {
        'title': path.basename(cmd_dict['data_dir']),
        'data_dir': cmd_dict['data_dir'],
        'job_log': cmd_dict['job_log'],
        'master_addr': master_addr,
        'slave_desc': cmd_dict['slave_desc'],
        'expt_time': expt_time,
        'time': cmd_dict['time'],
        'runs': cmd_dict['runs'],
        'scenario': cmd_dict['scenario'],
    }

    sender = cmd_dict['sender']
    if expt_type == 'node':
        d['node'] = slave
        d['cloud'] = master
        d['to_node'] = True if sender == 'local' else False
        d['link'] = cmd_dict['link']
    elif expt_type == 'cloud':
        if sender == 'local':
            d['src'] = master
            d['dst'] = slave
        else:
            d['src'] = slave
            d['dst'] = master

    analyze_and_upload(d)

    # cleanup
    utils.cleanup([master, slave])


def run_node(cellular_nodes, ethernet_nodes):
    sys.stderr.write('----- Running node-to-cloud experiments -----\n')

    # convert lists to sets for faster lookup
    cellular_nodes = set(cellular_nodes)
    ethernet_nodes = set(ethernet_nodes)

    cfg = utils.expt_cfg['node']
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
                if '{slave_cell_if}' in cmd_tmpl:
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


def run_cloud(hosts):
    sys.stderr.write('----- Running cloud-to-cloud experiments -----\n')

    # create a schedule for a "round-robin tournament" among live cloud servers
    schedule = round_robin_tournament.schedule(hosts)

    cfg = utils.expt_cfg['cloud']
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


# smallest unit of emulation experiment that will be run in parallel
def run_emu_experiment(emu_server, cmd_tmpl, job_cfg):
    # cleanup
    utils.cleanup([emu_server])

    # 4. fill in the remaining varialbes
    expt_time = utils.utc_date()
    cmd_dict = emu_server_expand(emu_server, cmd_tmpl, job_cfg, expt_time)
    cmd = utils.safe_format(cmd_tmpl, cmd_dict)

    emu_addr = utils.get_host_addr(emu_server)
    final_cmd = ['ssh', emu_addr, cmd]
    check_call(final_cmd)

    # prepare parameters used in analyze_and_upload
    d = {
        'title': path.basename(cmd_dict['data_dir']),
        'data_dir': cmd_dict['data_dir'],
        'job_log': cmd_dict['job_log'],
        'master_addr': emu_addr,
        'expt_time': expt_time,
        'time': cmd_dict['time'],
        'runs': cmd_dict['runs'],
        'scenario': cmd_dict['scenario'],
        'emu_scenario': job_cfg['scenario'],
        'emu_cmd': cmd_dict['mm_cmd'],
        'emu_desc': job_cfg['desc'],
    }

    analyze_and_upload(d)

    # cleanup
    utils.cleanup([emu_server])


def run_emu(hosts):
    sys.stderr.write('----- Running emulation experiments -----\n')

    cfg = utils.expt_cfg['emu']
    matrix = utils.expand_matrix(cfg['matrix'])

    # create a queue of jobs
    job_queue = deque()
    for mat_dict in matrix:
        for job_cfg in cfg['jobs']:
            cmd_tmpl = job_cfg['command']

            # 1. expand macros
            cmd_tmpl = utils.safe_format(cmd_tmpl, cfg['macros'])
            # 2. expand variables in mat_dict
            cmd_tmpl = utils.safe_format(cmd_tmpl, mat_dict)
            # 3. expand meta
            cmd_tmpl = utils.safe_format(cmd_tmpl, utils.meta)

            job_queue.append((job_cfg, cmd_tmpl))

    while len(job_queue):
        procs = []
        for emu_server in utils.host_cfg['emu_servers']:
            if len(job_queue) == 0:
                break

            job_cfg, cmd_tmpl = job_queue.popleft()
            p = Process(target=run_emu_experiment,
                        args=(emu_server, cmd_tmpl, job_cfg))
            p.start()
            procs.append(p)

        if procs:
            for p in procs:
                p.join()


def main():
    # get commands to run from experiments.yml
    parser = argparse.ArgumentParser()
    parser.add_argument('expt_type', choices=['node', 'cloud', 'emu'])
    parser.add_argument('--no-post', metavar='LOG',
        help='save POST payloads to LOG rather than post to the website')
    args = parser.parse_args()

    # change global variables
    global expt_type, no_post_log
    expt_type = args.expt_type
    no_post_log = args.no_post

    # start servers
    live_hosts = start_hosts()

    # run setup
    setup(live_hosts)

    if expt_type == 'node':
        live_ethernet_nodes = []
        nodes_with_cellular = []

        for node, node_cfg in utils.host_cfg['nodes'].iteritems():
            if node in live_hosts:
                live_ethernet_nodes.append(node)

                if 'cell_if' in node_cfg:
                    nodes_with_cellular.append(node)

        live_cellular_nodes = setup_cellular_links(nodes_with_cellular)

        run_node(live_cellular_nodes, live_ethernet_nodes)

    elif expt_type == 'cloud':
        run_cloud(live_hosts)

    elif expt_type == 'emu':
        run_emu(live_hosts)

    # stop servers
    stop_hosts()


if __name__ == '__main__':
    main()
