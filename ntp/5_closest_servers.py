#!/usr/bin/env python

import subprocess
import heapq
import random


server_to_delay = dict()

with open('working_stratum_1') as server_file:
    servers = server_file.read().splitlines()
    random.shuffle(servers)
    for server in servers:
        try:
            cmd = ['ntpdate', '-quv', server]
            print ' '. join(cmd)
            output_lines = subprocess.check_output(cmd).splitlines()
        except:
            continue
        best_delay = 11111.
        for line in output_lines:
            print line
            if line.startswith('server '):
                delay = abs(float(line.split()[-1]))
                if delay > 0.0001:
                    best_delay = min(best_delay, delay)
        server_to_delay[server] = best_delay
print(heapq.nsmallest(5, server_to_delay.iteritems(), key=(lambda (k, v): v)))
