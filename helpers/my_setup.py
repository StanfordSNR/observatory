#!/usr/bin/env python

import argparse
import colorama
from helpers import check_call, Popen


def aws_key_setup(host):
    cmd = (
        'KEY=$(cat ~/.ssh/id_rsa.pub); '
        'ssh -i ~/.ssh/fyy.pem -o StrictHostKeyChecking=no %s '
        '"grep -qF \'$KEY\' .ssh/authorized_keys || '
        'echo \'$KEY\' >> .ssh/authorized_keys"' % host)
    check_call(cmd, shell=True)

    cmd = (
        'KEY=$(cat ~/.ssh/pantheon_aws.pub); '
        'ssh %s '
        '"grep -qF \'$KEY\' .ssh/authorized_keys || '
        'echo \'$KEY\' >> .ssh/authorized_keys"' % host)
    check_call(cmd, shell=True)

    cmd = 'scp ~/.ssh/pantheon_aws %s:~/.ssh/id_rsa' % host
    check_call(cmd, shell=True)

    cmd = 'scp ~/.ssh/pantheon_aws.pub %s:~/.ssh/id_rsa.pub' % host
    check_call(cmd, shell=True)

    cmd = (
        'sudo apt-get update && '
        'sudo apt-get -y install python-minimal awscli')
    check_call(['ssh', host, cmd])


def clone_setup(host):
    cmd = 'scp ~/.vimrc %s:~' % host
    check_call(cmd, shell=True)

    cmd = 'scp ~/pantheon-observatory/helpers/bashrc %s:~/.bashrc' % host
    check_call(cmd, shell=True)

    cmd = ['ssh', '-t', host,
           'git clone https://github.com/StanfordSNR/pantheon.git && '
           'cd ~/pantheon && '
           'git checkout refactor && '
           './install_deps.sh && '
           './test/setup.py --all --install-deps && '
           './test/setup.py --all --setup']
    return Popen(cmd)


def run_cmd(host, cmd, procs):
    if cmd == 'aws_key_setup':
        aws_key_setup(host)
    elif cmd == 'clone_setup':
        procs.append(clone_setup(host))
    else:
        procs.append(Popen(['ssh', host, cmd]))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ip', required=True, metavar='"IP1,IP2..."',
        help='comma-separated list of IP addresses of remote hosts')
    parser.add_argument(
        '--user', default='ubuntu',
        help='username used in ssh and scp (default: ubuntu)')
    parser.add_argument(
        '--cmd', required=True, help='command to run')
    args = parser.parse_args()

    colorama.init()

    ip_list = args.ip.split(',')
    procs = []

    for ip in ip_list:
        host = args.user+ '@' + ip
        run_cmd(host, args.cmd, procs)

    for proc in procs:
        proc.wait()


if __name__ == '__main__':
    main()
