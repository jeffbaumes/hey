import datetime
import json
import os
import requests


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def DecodeDateTime(datum):
    for time_field in ['updated']:
        if time_field in datum:
            datum[time_field] = datetime.datetime.fromisoformat(datum[time_field])
    return datum


def save(data):
    if os.environ.get('HEY_JSONBIN_ID'):
        url = f'https://api.jsonbin.io/b/{os.environ.get("HEY_JSONBIN_ID")}'
        headers = {
            'Content-Type': 'application/json',
            'versioning': 'false',
            'secret-key': os.environ.get('HEY_JSONBIN_KEY')
        }
        req = requests.put(url, data=json.dumps(data, cls=DateTimeEncoder, indent=2), headers=headers)
    else:
        with open('data.json', 'w') as f:
            json.dump(data, f, cls=DateTimeEncoder, indent=2)


def load():
    if os.environ.get('HEY_JSONBIN_ID'):
        url = f'https://api.jsonbin.io/b/{os.environ.get("HEY_JSONBIN_ID")}'
        headers = {
            'secret-key': os.environ.get('HEY_JSONBIN_KEY')
        }
        req = requests.get(url, headers=headers)
        data = json.loads(req.text, object_hook=DecodeDateTime)
    else:
        try:
            with open('data.json') as f:
                data = json.load(f, object_hook=DecodeDateTime)
        except FileNotFoundError:
            data = []
            save(data)
    return data
