import sys
from os import path
import subprocess
from datetime import datetime
from time import strftime
import yaml
import project_root


def print_cmd(cmd):
    if isinstance(cmd, list):
        cmd_to_print = ' '.join(cmd).strip()
    elif isinstance(cmd, str) or isinstance(cmd, unicode):
        cmd_to_print = cmd.strip()
    else:
        cmd_to_print = ''

    if cmd_to_print:
        sys.stderr.write('$ %s\n' % cmd_to_print)


def call(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.call(cmd, **kwargs)


def check_call(cmd, **kwargs):
    print_cmd(cmd)
    # return subprocess.check_call(cmd, **kwargs)


def check_output(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.check_output(cmd, **kwargs)


def Popen(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.Popen(cmd, **kwargs)


def parse_config():
    with open(path.join(project_root.DIR, 'vantage_points.yml')) as config:
        return yaml.load(config)


def update_submodules():
    cmd = 'git submodule update --init --recursive'
    check_call(cmd, shell=True)


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError()


def format_time():
    return strftime('%a, %d %b %Y %H:%M:%S %z')


def utc_date():
    return datetime.utcnow().strftime('%Y-%m-%dT%H-%M')


def run_cmd_on_hosts(cmd, hosts, sync=False):
    if sync:
        for host in hosts:
            check_call(['ssh', host, cmd])
    else:
        procs = [Popen(['ssh', host, cmd]) for host in hosts]
        for proc in procs:
            proc.wait()
