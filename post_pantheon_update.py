#!/usr/bin/env python

import os
import requests

update_url = os.environ['UPDATE_URL']
# url = 'http://52.8.182.100/%s/' % update_url
url = 'http://127.0.0.1:8000/%s/' % update_url

client = requests.session()
response = client.get(url)

csrftoken = client.cookies['csrftoken']

node = 'stanford'

prefix = 'https://s3.amazonaws.com/stanford-pantheon/real-world/%s/' % node
payload = {
    'csrfmiddlewaretoken': csrftoken,
    'node': node,
    'link': 'cellular',
    'to_node': True,
    'data': 'fake_data',
    'report': 'fake_report',
    'summary': 'fake_summary',
    'summary_mean': 'fake_summary_mean',
    'time': '2017-04-12T21-50',
}

client.post(url, data=payload, headers=dict(Referer=url))
