#!/usr/bin/env python

import subprocess
import random


try:
    cmd = ['ntpdate', '-quv', 'clock.tl.fukuoka-u.ac.jp']
    print ' '. join(cmd)
    output = subprocess.check_output(cmd)
except:
    print 'except'
if output.find('stratum 1,'):
    print 'good'
else:
    print server + " not stratum 1"
