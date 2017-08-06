#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import Popen, check_call, wait_procs


def main():
    assistant = path.join(project_root.DIR, 'assistant.py')
    console = path.join(project_root.DIR, 'console.py')

    check_call([assistant, '--gce-servers', '-c', 'pkill'])
    check_call([assistant, '--gce-servers', '-c', 'setup'])

    base_cmd = [console, 'cloud', '--all', '--run-times', '10']

    # first round
    procs = []
    procs.append(Popen(base_cmd + ['gce_iowa', 'gce_sydney']))
    procs.append(Popen(base_cmd + ['gce_london', 'gce_tokyo']))
    wait_procs(procs)

    # second round
    procs = []
    procs.append(Popen(base_cmd + ['gce_iowa', 'gce_london']))
    procs.append(Popen(base_cmd + ['gce_sydney', 'gce_tokyo']))
    wait_procs(procs)

    # third round
    procs = []
    procs.append(Popen(base_cmd + ['gce_iowa', 'gce_tokyo']))
    procs.append(Popen(base_cmd + ['gce_sydney', 'gce_london']))
    wait_procs(procs)


if __name__ == '__main__':
    main()
