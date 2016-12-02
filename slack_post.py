#! /usr/bin/python3
import requests
import json
from os import path

def slack_post(text):
    try:
        this_dir = path.dirname(__file__)
        secret_url_file = path.join(this_dir, '.secret_slack_url')

        with open(secret_url_file, 'r') as f:
            secret_slack_url = f.readline()

        payload = { 'text': text }
        r = requests.post(secret_slack_url, data=json.dumps(payload))
        print("Slack POST returned " + str(r.status_code) +": " + r.text)
    except Exception as e:
        print("Slack integration failed to post: " + str(e))
