#!/usr/bin/env python

import subprocess
import random


with open('working_stratum_1', 'w') as out_file:
    with open('all_stratum_1') as server_file:
        servers = server_file.read().splitlines()
        random.shuffle(servers)
        for server in servers:
            try:
                cmd = ['ntpdate', '-quv', server]
                print ' '. join(cmd)
                output_lines = subprocess.check_output(cmd).splitlines()
                out_file.write(server + '\n')
            except:
                continue
