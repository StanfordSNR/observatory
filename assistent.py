#!/usr/bin/env python

import argparse
from helpers.helpers import check_call, Popen, parse_config


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
           'sudo apt-get -y install python-minimal awscli')
    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def nodes_key_setup(host):
    cmd = ('KEY=$(cat ~/.ssh/pantheon_aws.pub); '
           'ssh -o StrictHostKeyChecking=no %s '
           '"grep -qF \'$KEY\' .ssh/authorized_keys || '
           'echo \'$KEY\' >> .ssh/authorized_keys"' % host)
    return Popen(cmd, shell=True)


def clone_setup(host):
    cmd = ('git clone https://github.com/StanfordSNR/pantheon.git && '
           'cd ~/pantheon && '
           'git checkout refactor && '
           './install_deps.sh && '
           './test/setup.py --all --install-deps && '
           './test/setup.py --all --setup')
    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def config_copy(host):
    cmd = 'mkdir -p ~/.ssh/controlmasters'
    check_call(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])

    cmd = 'scp ~/.vimrc %s:~' % host
    check_call(cmd, shell=True)

    helpers_dir = '~/pantheon-observatory/helpers'
    cmd = 'scp %s/bashrc %s:~/.bashrc' % (helpers_dir, host)
    check_call(cmd, shell=True)

    cmd = 'scp %s/ssh_config %s:~/.ssh/config' % (helpers_dir, host)
    check_call(cmd, shell=True)


def pkill(host):
    cmd = '~/pantheon/helpers/pkill.py --kill-dir ~/pantheon'
    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])


def git_pull(host, force=False):
    if not force:
        cmd = 'cd ~/pantheon && git checkout refactor && git pull'
    else:
        cmd = ('cd ~/pantheon && git checkout refactor && '
               'git reset --hard @ && git pull')

    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd])

def run_cmd(args, host, procs):
    cmd = args.cmd

    if cmd == 'aws_key_setup':
        procs.append(aws_key_setup(host, args.i))
    elif cmd == 'clone_setup':
        procs.append(clone_setup(host))
    elif cmd == 'config_copy':
        config_copy(host)
    elif cmd == 'nodes_key_setup':
        procs.append(nodes_key_setup(host))
    elif cmd == 'pkill':
        procs.append(pkill(host))
    elif cmd == 'git_pull':
        procs.append(git_pull(host))
    elif cmd == 'git_force_pull':
        procs.append(git_pull(host, force=True))
    else:
        procs.append(
            Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, cmd]))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--all', action='store_true',
        help='all hosts listed in config.yml')
    parser.add_argument(
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
        'cmd', help='aws_key_setup, nodes_key_setup, clone_setup, config_copy,'
        ' pkill, git_pull, git_force_pull, etc.')
    args = parser.parse_args()

    procs = []

    if args.all:
        config = parse_config()

        for machine_type in config:
            for location in config[machine_type]:
                site = config[machine_type][location]
                host = site['user'] + '@' + site['addr']
                run_cmd(args, host, procs)
    elif args.hosts is not None:
        config = parse_config()

        hosts = args.hosts.split(',')
        for machine_type in config:
            for location in config[machine_type]:
                if location not in hosts:
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
