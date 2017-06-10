#!/usr/bin/env python

import argparse
from helpers.helpers import check_call, call, Popen, parse_config


def aws_key_setup(host, ssh_identity):
    cmd = ('KEY=$(cat ~/.ssh/id_rsa.pub); '
           'ssh -i %s -o StrictHostKeyChecking=no %s '
           '"grep -qF \'$KEY\' .ssh/authorized_keys || '
           'echo \'$KEY\' >> .ssh/authorized_keys"' % (ssh_identity, host))
    check_call(cmd, shell=True)

    cmd = ('KEY=$(cat ~/.ssh/pantheon_aws.pub); '
           'ssh %s '
           '"grep -qF \'$KEY\' .ssh/authorized_keys || '
           'echo \'$KEY\' >> .ssh/authorized_keys"' % host)
    check_call(cmd, shell=True)

    cmd = 'scp ~/.ssh/pantheon_aws %s:~/.ssh/id_rsa' % host
    check_call(cmd, shell=True)

    cmd = 'scp ~/.ssh/pantheon_aws.pub %s:~/.ssh/id_rsa.pub' % host
    check_call(cmd, shell=True)

    cmd = ('sudo apt-get update && '
           'sudo apt-get -y install python-minimal awscli && '
           'sudo pip install requests')
    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def add_pantheon_key(host):
    cmd = ('KEY=$(cat ~/.ssh/pantheon_aws.pub); '
           'ssh -o StrictHostKeyChecking=no %s '
           '"grep -qF \'$KEY\' .ssh/authorized_keys || '
           'echo \'$KEY\' >> .ssh/authorized_keys"' % host)
    return Popen(cmd, shell=True)


def clone_setup(host):
    cmd = ('git clone https://github.com/StanfordSNR/pantheon.git && '
           'cd ~/pantheon && '
           './install_deps.sh && '
           './test/setup.py --all --install-deps && '
           './test/setup.py --all --setup')
    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def copy_ssh_config(host):
    helpers_dir = '~/observatory/helpers'
    cmd = 'scp -o StrictHostKeyChecking=no %s/ssh_config %s:~/.ssh/config' % (
        helpers_dir, host)
    check_call(cmd, shell=True)


def copy_rc(host):
    cmd = 'scp -o StrictHostKeyChecking=no ~/.vimrc %s:~' % host
    check_call(cmd, shell=True)

    helpers_dir = '~/observatory/helpers'
    cmd = 'scp -o StrictHostKeyChecking=no %s/bashrc %s:~/.bashrc' % (
        helpers_dir, host)
    check_call(cmd, shell=True)


def pkill(host):
    cmd = '~/pantheon/helpers/pkill.py'
    call(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])

    cmd = 'rm -rf /tmp/2017-*-run* /tmp/pantheon-tmp'
    call(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def git_pull(host, force=False):
    if not force:
        cmd = 'cd ~/pantheon && git pull'
    else:
        cmd = 'cd ~/pantheon && git reset --hard @ && git pull'

    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def ssh_key_remove(host):
    ip = host.split('@')[-1]
    cmd = 'ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R ' + ip
    check_call(cmd, shell=True)


def run_cmd(args, host, procs):
    cmd = args.cmd

    if cmd == 'aws_key_setup':
        procs.append(aws_key_setup(host, args.i))
    elif cmd == 'clone_setup':
        procs.append(clone_setup(host))
    elif cmd == 'copy_ssh_config':
        copy_ssh_config(host)
    elif cmd == 'copy_rc':
        copy_rc(host)
    elif cmd == 'add_pantheon_key':
        procs.append(add_pantheon_key(host))
    elif cmd == 'pkill':
        pkill(host)
    elif cmd == 'git_pull':
        procs.append(git_pull(host))
    elif cmd == 'git_force_pull':
        procs.append(git_pull(host, force=True))
    elif cmd == 'ssh_key_remove':
        ssh_key_remove(host)
    else:
        procs.append(
            Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd]))


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--all', action='store_true',
        help='all hosts listed in config.yml')
    group.add_argument(
        '--measurement-nodes', action='store_true',
        help='all measurement nodes listed in config.yml')
    group.add_argument(
        '--cloud-servers', action='store_true',
        help='all cloud servers listed in config.yml')
    group.add_argument(
        '--hosts', metavar='"HOST1,HOST2..."',
        help='comma-separated list of hosts listed in config.yml')

    parser.add_argument(
        '--ip', metavar='"IP1,IP2..."',
        help='comma-separated list of IP addresses of remote hosts')
    parser.add_argument(
        '--user', default='ubuntu',
        help='username used in ssh and scp (default: ubuntu)')
    parser.add_argument(
        '-i', metavar='identify_file', help='ssh identity file')
    parser.add_argument(
        'cmd', help='aws_key_setup, add_pantheon_key, clone_setup, '
        'copy_ssh_config, copy_rc, pkill, git_pull, git_force_pull, '
        'ssh_key_remove, etc.')
    args = parser.parse_args()

    procs = []

    hosts = None
    if args.hosts is not None:
        hosts = args.hosts.split(',')

    if (args.all or args.measurement_nodes or args.cloud_servers or
            hosts is not None):
        config = parse_config()

        for machine_type in config:
            if hosts is None:
                if machine_type == 'measurement_nodes':
                    if not args.all and not args.measurement_nodes:
                        continue

                if machine_type == 'cloud_servers':
                    if not args.all and not args.cloud_servers:
                        continue

            for location in config[machine_type]:
                if hosts is not None and location not in hosts:
                    continue

                site = config[machine_type][location]
                host = site['user'] + '@' + site['addr']
                run_cmd(args, host, procs)
    else:
        ip_list = args.ip.split(',')

        for ip in ip_list:
            host = args.user + '@' + ip
            run_cmd(args, host, procs)

    for proc in procs:
        proc.wait()


if __name__ == '__main__':
    main()
