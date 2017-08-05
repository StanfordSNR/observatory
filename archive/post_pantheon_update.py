#!/usr/bin/env python

import os
import requests

update_url = os.environ['UPDATE_URL']
url = 'http://localhost:8000/%s/emu/' % update_url

client = requests.session()
response = client.get(url)

csrftoken = client.cookies['csrftoken']

'''
payload = {
    'csrfmiddlewaretoken': csrftoken,
    'node': 'nepal',
    'cloud': 'aws_india',
    'to_node': True,
    'link': 'wireless',
    'flow': 3,
    'time_created': '2018-04-12T21-50',
    'log': 'fake_log',
    'report': 'fake_report',
    'graph1': 'fake_graph1',
    'graph2': 'fake_graph2',
}
'''

'''
payload = {
    'csrfmiddlewaretoken': csrftoken,
    'src': 'gce_oregon',
    'dst': 'gce_tokyo',
    'flow': 3,
    'time_created': '2018-08-12T21-50',
    'log': 'fake_log',
    'report': 'fake_report',
    'graph1': 'fake_graph1',
    'graph2': 'fake_graph2',
}
'''

payload = {
    'csrfmiddlewaretoken': csrftoken,
    'emu_cmd': 'mm-delay 25',
    'desc': 'imitation game',
    'flow': 3,
    'time_created': '2018-10-29T21-50',
    'log': 'fake_log',
    'report': 'fake_report',
    'graph1': 'fake_graph1',
    'graph2': 'fake_graph2',
}

client.post(url, data=payload, headers=dict(Referer=url))
