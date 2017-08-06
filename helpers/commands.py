from helpers import run_cmd_on_hosts, Popen


def clone_setup(hosts):
    cmd = ('sudo apt-get update && '
           'sudo apt-get -y install python-minimal python-pip pxz awscli && '
           'sudo pip install requests && '
           'git clone https://github.com/StanfordSNR/pantheon.git && '
           'cd ~/pantheon && '
           './install_deps.sh && '
           './test/setup.py --all --install-deps && '
           './test/setup.py --all --setup')
    run_cmd_on_hosts(cmd, hosts)


def git_pull(hosts):
    cmd = 'cd ~/pantheon && git pull'
    run_cmd_on_hosts(cmd, hosts)


def pkill(hosts):
    cmd = ('rm -rf ~/pantheon_data /tmp/pantheon-tmp; '
           'python ~/pantheon/helpers/pkill.py; '
           'sudo sysctl -w net.core.default_qdisc=pfifo_fast; '
           'pkill -f pantheon')
    run_cmd_on_hosts(cmd, hosts)


def setup(hosts):
    cmd = 'cd ~/pantheon && git pull && ./test/setup.py --all --setup'
    run_cmd_on_hosts(cmd, hosts)


def setup_ppp0(hosts):
    cmd = ('cd ~/pantheon && git pull && '
           './test/setup.py --all --setup --interface ppp0')
    run_cmd_on_hosts(cmd, hosts)


def add_pub_key(hosts):
    key = raw_input()

    procs = []
    for host in hosts:
        cmd = ('KEY=\'%s\'; '
               'ssh %s '
               '"grep -qF \'$KEY\' .ssh/authorized_keys || '
               'echo \'$KEY\' >> .ssh/authorized_keys"' % (key, host))
        procs.append(Popen(cmd, shell=True))

    for proc in procs:
        proc.wait()


def ssh_each_other(hosts):
    procs = []

    for host1 in hosts:
        for host2 in hosts:
            if host1 != host2:
                cmd = 'ssh -o StrictHostKeyChecking=no %s date' % host2
                procs.append(Popen(['ssh', host1, cmd]))

    for proc in procs:
        proc.wait()
