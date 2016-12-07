#! /usr/bin/python3
import json
from os import path
import requests


# helper
def get_slack_url():
    try:
        this_dir = path.dirname(__file__)
        secret_url_file = path.join(this_dir, '.secret_slack_url')

        with open(secret_url_file, 'r') as f:
            secret_slack_url = f.readline()
        return secret_slack_url
    except Exception as e:
        print("Slack integration failed to read secret url: " + str(e))


# helper
def slack_post_json(json_string):
    secret_slack_url = get_slack_url()
    try:
        r = requests.post(secret_slack_url, data=json_string)
        print("Slack POST returned " + str(r.status_code) + ": " + r.text)
    except Exception as e:
        print("Slack integration failed to post: " + str(e))


def slack_post(text):
    payload = {'text': text}
    slack_post_json(json.dumps(payload))


def slack_post_img(title, img_url):
    payload = {'text': title, 'attachments': [{'image_url': img_url}]}
    slack_post_json(json.dumps(payload))
