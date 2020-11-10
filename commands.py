import datetime
import random
import webbrowser

from app import App
from data import load, save


app = App()
data = load()

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

@app.route(r'i (should maybe|might want to|maybe want to) do( task)? <task_num>')
def maybe_do_existing_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'maybe')
    save(data)
    return f'got it. i set that task to maybe'

@app.route(r'i (should maybe|might want to|maybe want to) <task>')
def maybe(task):
    data.append(dict(type='task', name=task, state='maybe', updated=datetime.datetime.now()))
    save(data)
    return f'sure, i added a maybe task. "{len(data) - 1}: {task}"'

@app.route(r'i (want to|need to|should) do( task)? <task_num>')
def do_existing_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'do')
    save(data)
    return f'got it. i set that as an active task for you to do'

@app.route(r'i (want to|need to|should) <task>')
def add_task(task):
    data.append(dict(type='task', name=task, state='do', updated=datetime.datetime.now()))
    save(data)
    return f'sure, you now have a task "{len(data) - 1}: {task}"'

@app.route(r'what should i do')
@app.route(r'what do i need to do')
def todo_list():
    return 'you should:\n{}'.format('\n'.join([
        f'{i}: {d["name"]}' for i, d in query_data('task', 'do')
    ]))

@app.route(r'what did i do')
def completed_list():
    return 'you did:\n{}'.format('\n'.join([
        f'{i}: {d["name"]}' for i, d in query_data('task', 'done')
    ]))

@app.route(r'what am i waiting (on|for)')
def waiting_list():
    return 'you are waiting for:\n{}'.format('\n'.join([
        f'{i}: {d["name"]} ({d["who"]})' for i, d in query_data('task', 'waiting')
    ]))

@app.route(r'what should i maybe do')
@app.route(r'what is on my maybe list')
def todo_list():
    return 'you should maybe:\n{}'.format('\n'.join([
        f'{i}: {d["name"]}' for i, d in query_data('task', 'maybe')
    ]))

@app.route(r'i did( task)? <task_num>')
@app.route(r'(task )?<task_num> is done')
def complete_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'done')
    save(data)
    return f'{good_job()} i checked off task "{task["name"]}"'

@app.route(r'i didn\'t do( task)? <task_num>')
@app.route(r'(task )?<task_num> is not done')
def uncomplete_task(task_num):
    task_num = int(task_num)
    task = data[task_num]
    update_state(task, 'waiting' if task.get('who') else 'do')
    save(data)
    return f'oh ok fine, i made task "{task["name"]}" active'

@app.route(r'open( the)? link for <task_num>')
def open_link(task_num):
    task_num = int(task_num)
    task = data[task_num]
    if 'link' in task:
        webbrowser.open(task['link'])
        return 'ok'
    return 'um, i don\'t have a link for that task'

@app.route(r'(the )?link for( task)? <task_num> is <url>')
@app.route(r'(task )?<task_num> has link <url>')
def set_link(task_num, url):
    task_num = int(task_num)
    task = data[task_num]
    task['link'] = url
    save(data)
    return 'got it. the link is updated'

@app.route(r'<who> (should|needs to) do( task)? <task_num>')
@app.route(r'(i need|i\'m waiting for) <who> to do( task)? <task_num>')
def waiting_on_existing_task(who, task_num):
    task_num = int(task_num)
    task = data[task_num]
    task['who'] = who
    update_state(task, 'waiting')
    save(data)
    return f'got it. you are waiting for {who} to complete that task'

@app.route(r'<who> (should|needs to) <task>')
@app.route(r'(i need|i\'m waiting for) <who> to <task>')
def waiting(who, task):
    data.append(dict(type='task', name=task, who=who, state='waiting', updated=datetime.datetime.now()))
    save(data)
    return f'sure, i recorded this new task that you\'re waiting for. "{len(data) - 1}: {task}"'

@app.route(r'bye')
def bye():
    return 'bye'

@app.route(r'<any>')
def default(any):
    return 'ok... not really sure what you mean by that'
