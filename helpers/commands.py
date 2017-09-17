import project_root
from os import path
from helpers import run_cmd_on_hosts, Popen, wait_procs, call


def install_deps(hosts):
    cmd = ('sudo apt-get update && '
           'sudo apt-get -y install python-minimal python-pip pxz awscli && '
           'sudo pip install requests')
    run_cmd_on_hosts(cmd, hosts)


def clone_pantheon(hosts):
    cmd = ('git clone https://github.com/StanfordSNR/pantheon.git && '
           'cd ~/pantheon && '
           './install_deps.sh && '
           './test/setup.py --all --install-deps && '
           './test/setup.py --all --setup')
    run_cmd_on_hosts(cmd, hosts)


def git_pull(hosts):
    cmd = 'cd ~/pantheon && git pull'
    run_cmd_on_hosts(cmd, hosts)


def cleanup(hosts):
    cmd = ('rm -rf ~/pantheon_data /tmp/pantheon-tmp; '
           'python ~/pantheon/helpers/pkill.py; '
           'pkill -f pantheon')
    run_cmd_on_hosts(cmd, hosts)


def setup(hosts):
    cmd = ('sudo sysctl -w net.core.default_qdisc=pfifo_fast; '
           'cd ~/pantheon && git pull && ./test/setup.py --all --setup')
    run_cmd_on_hosts(cmd, hosts)


def setup_ppp0(hosts):
    cmd = 'cd ~/pantheon && ./test/setup.py --interface ppp0'
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

    wait_procs(procs)


def copy_ssh_config(hosts):
    ssh_config = path.join(project_root.DIR, 'helpers', 'config')

    procs = []
    for host in hosts:
        cmd = ['scp', ssh_config, '%s:~/.ssh/config' % host]
        procs.append(Popen(cmd))

    wait_procs(procs)


def mount_readwrite(hosts):
    cmd = 'sudo ~/mount_readwrite.sh'
    run_cmd_on_hosts(cmd, hosts)


def remove_key(hosts):
    known_hosts = path.expanduser('~/.ssh/known_hosts')

    for host in hosts:
        ip = host.split('@')[1].strip()
        cmd = 'ssh-keygen -f "%s" -R ' % known_hosts + ip
        call(cmd, shell=True)


def test_ssh(hosts):
    for host in hosts:
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                '-o', 'ConnectTimeout=5', host, 'echo $HOSTNAME']
        call(cmd)
