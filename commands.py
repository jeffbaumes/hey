import datetime
import json
import os
import random
import re
import requests
import webbrowser

class App():
    def __init__(self):
        self.routes = []

    @staticmethod
    def build_route_pattern(route):
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{}$".format(route_regex))

    def route(self, route_str):
        def decorator(f):
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, f))

            return f

        return decorator

    def get_route_match(self, path):
        for route_pattern, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), view_function

        return None

    def serve(self, path):
        route_match = self.get_route_match(path)
        if route_match:
            kwargs, view_function = route_match
            return view_function(**kwargs)
        else:
            raise ValueError('Route "{}"" has not been registered'.format(path))


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

def DecodeDateTime(datum):
    for time_field in ['created', 'completed', 'due']:
        if time_field in datum:
            datum[time_field] = datetime.datetime.fromisoformat(datum[time_field])
    return datum

def save():
    if os.environ.get('HEY_JSONBIN_ID'):
        url = f'https://api.jsonbin.io/b/{os.environ.get("HEY_JSONBIN_ID")}'
        headers = {
            'Content-Type': 'application/json',
            'versioning': 'false',
            'secret-key': os.environ.get('HEY_JSONBIN_KEY')
        }
        req = requests.put(url, data=json.dumps(data, cls=DateTimeEncoder, indent=2), headers=headers)
    else:
        with open('facts.json', 'w') as f:
            json.dump(data, f, cls=DateTimeEncoder, indent=2)

def update_state(task, state):
    task['state'] = state
    task['updated'] = datetime.datetime.now()

def good_job():
    responses = [
        'excellent!',
        'nice!',
        'good job!',
        'way to go!',
        'alright!',
        'congrats!',
    ]
    return responses[random.randrange(0, len(responses))]

def query_data(datatype=None, state=None):
    return [(i, d) for (i, d) in enumerate(data) if (
        (datatype is None or d['type'] == datatype) and
        (state is None or d['state'] == state)
    )]


app = App()

data = []
if os.environ.get('HEY_JSONBIN_ID'):
    url = f'https://api.jsonbin.io/b/{os.environ.get("HEY_JSONBIN_ID")}'
    headers = {
        'secret-key': os.environ.get('HEY_JSONBIN_KEY')
    }
    req = requests.get(url, headers=headers)
    data = json.loads(req.text, object_hook=DecodeDateTime)
else:
    try:
        with open('facts.json') as f:
            data = json.load(f, object_hook=DecodeDateTime)
    except FileNotFoundError:
        save()

@app.route("i'm <name>")
@app.route("i am <name>")
def hello_user(name):
    return 'hello {}'.format(name)

@app.route('i should maybe do <task_num>')
@app.route('i might want to do <task_num>')
@app.route('i maybe want to do <task_num>')
@app.route('i should maybe do task <task_num>')
@app.route('i might want to do task <task_num>')
@app.route('i maybe want to do task <task_num>')
def maybe_do_existing_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'maybe')
    save()
    return f'got it. i set that task to maybe'

@app.route('i should maybe <task>')
@app.route('i might want to <task>')
@app.route('i maybe want to <task>')
def maybe(task):
    data.append(dict(type='task', name=task, state='maybe', updated=datetime.datetime.now()))
    save()
    return f'sure, i added a maybe task. "{len(data) - 1}: {task}"'

@app.route('i want to <task>')
@app.route('i need to <task>')
@app.route('i should <task>')
def add_task(task):
    data.append(dict(type='task', name=task, state='do', updated=datetime.datetime.now()))
    save()
    return f'sure, you now have a task "{len(data) - 1}: {task}"'

@app.route('what should i do')
@app.route('what do i need to do')
def todo_list():
    return 'you should:\n{}'.format('\n'.join([
        f'{i}: {d["name"]}' for i, d in query_data('task', 'do')
    ]))

@app.route('what did i do')
def completed_list():
    return 'you did:\n{}'.format('\n'.join([
        f'{i}: {d["name"]}' for i, d in query_data('task', 'done')
    ]))

@app.route('what am i waiting on')
@app.route('what am i waiting for')
def waiting_list():
    return 'you are waiting for:\n{}'.format('\n'.join([
        f'{i}: {d["name"]} ({d["who"]})' for i, d in query_data('task', 'waiting')
    ]))

@app.route('what should i maybe do')
def todo_list():
    return 'you should maybe:\n{}'.format('\n'.join([
        f'{i}: {d["name"]}' for i, d in query_data('task', 'maybe')
    ]))

@app.route('i did <task_num>')
@app.route('i did task <task_num>')
@app.route('<task_num> is done')
@app.route('task <task_num> is done')
def complete_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'done')
    save()
    return f'{good_job()} i checked off task "{task["name"]}"'

@app.route('i didn\'t do <task_num>')
@app.route('i didn\'t do task <task_num>')
@app.route('<task_num> is not done')
@app.route('task <task_num> is not done')
def uncomplete_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'waiting' if task.get('who') else 'do')
    save()
    return f'oh ok fine, i unchecked task "{task["name"]}"'

@app.route('open link for <task_num>')
@app.route('open the link for <task_num>')
def open_link(task_num):
    task_num = int(task_num)
    task = data[task_num]
    if 'link' in task:
        webbrowser.open(task['link'])
        return 'ok'
    return 'um, i don\'t have a link for that task'

@app.route('link for <task_num> is <url>')
@app.route('the link for <task_num> is <url>')
@app.route('task <task_num> has link <url>')
def set_link(task_num, url):
    task_num = int(task_num)
    task = data[task_num]
    task['link'] = url
    save()
    return 'got it. the link is updated'

@app.route('<who> needs to do <task_num>')
@app.route('i need <who> to do <task_num>')
@app.route('i\'m waiting for <who> to do <task_num>')
@app.route('<who> should do <task_num>')
@app.route('<who> needs to do task <task_num>')
@app.route('i need <who> to do task <task_num>')
@app.route('i\'m waiting for <who> to do task <task_num>')
@app.route('<who> should do task <task_num>')
def waiting_on_existing_task(who, task_num):
    task_num = int(task_num)
    task = data[task_num]
    task['who'] = who
    update_state(task, 'waiting')
    save()
    return f'got it. you are waiting for {who} to complete that task'

@app.route('<who> needs to <task>')
@app.route('i need <who> to <task>')
@app.route('i\'m waiting for <who> to <task>')
@app.route('<who> should <task>')
def waiting(who, task):
    data.append(dict(type='task', name=task, who=who, state='waiting', updated=datetime.datetime.now()))
    save()
    return f'sure, i recorded this new task that you\'re waiting for. "{len(data) - 1}: {task}"'

@app.route('bye')
def bye():
    return 'bye'

@app.route('<any>')
def default(any):
    return 'ok'

