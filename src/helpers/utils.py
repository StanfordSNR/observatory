import sys
from os import path
import yaml
import time

import context
from helpers.subprocess_wrappers import check_call, Popen, call


def parse_vantage_points():
    with open(path.join(context.base_dir, 'vantage_points.yml')) as cfg:
        return yaml.load(cfg)


def parse_experiments():
    with open(path.join(context.scripts_dir, 'experiments.yml')) as cfg:
        return yaml.load(cfg)


host_cfg = parse_vantage_points()
expt_cfg = parse_experiments()
meta = expt_cfg['metadata']


def get_host_cfg(host):
    for host_type in host_cfg:
        if host in host_cfg[host_type]:
            return host_cfg[host_type][host]

    sys.exit('Error: invalid host ' + host)


def get_host_addr(host):
    host_cfg = get_host_cfg(host)
    return host_cfg['user'] + '@' + host_cfg['ip']


def ssh_cmd(host):
    addr = get_host_addr(host)
    return ['ssh', '-q', '-o', 'BatchMode=yes',
            '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5', addr]


def execute(host_cmd):
    """ Given 'host_cmd' with form: {host: command_to_run_over_SSH, ...},
        return {host: boolean (indicating success or failure), ... }
    """

    host_proc = {}
    for host, cmd in host_cmd.iteritems():
        host_proc[host] = Popen(ssh_cmd(host) + [cmd])

    for host in host_proc:
        host_proc[host] = True if host_proc[host].wait() == 0 else False

    return host_proc


def simple_execute(hosts, cmd):
    return execute({host:cmd for host in hosts})


def execute_retry(host_cmd, retry_times=0, retry_timeout=0):
    if retry_times > 0 and retry_timeout == 0:
        sys.exit('retry timeout must not be 0 if retry times is not 0')

    ret = {}
    for host in host_cmd:
        ret[host] = False
    failed_host_cmd = host_cmd.copy()

    retry = 0
    while True:
        host_status = execute(failed_host_cmd)
        for host, status in host_status.iteritems():
            if status:
                ret[host] = True
                failed_host_cmd.pop(host)

        # all commands have succeeded in running
        if not failed_host_cmd:
            return ret

        if retry >= retry_times:
            break
        else:
            time.sleep(retry_timeout)
            retry += 1

    return ret


def check_ssh_connection(hosts, retry_times=0, retry_timeout=0):
    host_cmd = {host:'exit' for host in hosts}
    return execute_retry(host_cmd, retry_times, retry_timeout)


def check_ppp0_connection(hosts, retry_times=0, retry_timeout=0):
    host_cmd = {host:'ping -I ppp0 -c 3 8.8.8.8' for host in hosts}
    return execute_retry(host_cmd, retry_times, retry_timeout)


def run_pppd(hosts):
    host_cmd = {host:'sudo pon %s' % host for host in hosts}
    return execute(host_cmd)


def setup_ppp0_interface(hosts):
    cmd = setup_system_path + ' --interface ppp0'
    return simple_execute(hosts, cmd)


def update_repository(hosts):
    cmd = ('cd {base_dir} && '
           'git fetch --all && '
           'git reset --hard origin/{branch} && '
           'git submodule update --init --recursive'
           .format(base_dir=meta['base_dir'], branch=meta['branch']))
    return simple_execute(hosts, cmd)


def cleanup(hosts):
    cmd = ('rm -rf {base_dir}/tmp && '
           '{pkill_path} --kill-dir {base_dir}'
           .format(base_dir=meta['base_dir'], pkill_path=meta['pkill_path']))
    return simple_execute(hosts, cmd)


def setup_system(hosts):
    cmd = ('{setup_system_path} --enable-ip-forwarding && '
           '{setup_system_path} --set-rmem'
           .format(setup_system_path=meta['setup_system_path']))
    return simple_execute(hosts, cmd)


def setup_after_reboot(hosts):
    cmd = '{setup_path} --all'.format(setup_path=meta['setup_path'])
    return simple_execute(hosts, cmd)
