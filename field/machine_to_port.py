#!/usr/bin/python

import sys

base_port = 11738
host_to_port = {

'lilbox0': base_port ,
'pi'     : base_port + 2

 }

if len( sys.argv ) is not 2:
    raise ValueError("Usage: " + sys.argv[0] + " hostname")

hostname = sys.argv[1] #TODO .tolower()
if hostname in host_to_port:
    print host_to_port[hostname]
else:
    raise ValueError("unknown hostname: " + hostname)
    #print ( hash(hostname) % 63499 ) + 2000 # chose port between 2000, 65499 based on the first 64 bits of the md5sum of the case-insensitive hostname (63499 is a prime number)
