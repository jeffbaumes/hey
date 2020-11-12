import datetime
import random
from tabulate import tabulate
from urllib.parse import urlparse
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

def query_data(datatype=None, state=None, context=None, who=None):
    return [dict(**d, id=i) for (i, d) in enumerate(data) if (
        (datatype is None or d.get('type') == datatype) and
        (state is None or d.get('state') == state) and
        (context is None or d.get('context') == context) and
        (who is None or d.get('who') == who)
    )]

def print_tasks(tasks):
    task_table = []
    for task in tasks:
        try:
            domain = urlparse(task.get('link', '')).netloc
        except:
            domain = ''
        
        try:
            updated = str(task['updated'].date())
        except:
            updated = ''

        row = [
            task['id'],
            task['name'],
            task.get('state', ''),
            task.get('context', ''),
            task.get('who', ''),
            updated,
            domain
        ]
        task_table.append(row)
    fields = ['id', 'name', 'state', 'context', 'who', 'updated', 'link']
    return tabulate(task_table, headers=fields)

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

@app.route(r'i (want to|need to|should) talk to <who> about <task_name>')
def add_task(who, task_name):
    task = dict(type='task', name=task_name, who=who)
    update_state(task, 'waiting')
    data.append(task)
    save(data)
    return f'sure, you now have a waiting task "{len(data) - 1}: {task_name}"'

@app.route(r'i (want to|need to|should) <task_name>')
@app.route(r'i (want to|need to|should) <task_name> for <context>')
def add_task(task_name, context=''):
    task = dict(type='task', name=task_name, context=context)
    update_state(task, 'do')
    data.append(task)
    save(data)
    return f'sure, you now have a task "{len(data) - 1}: {task_name}"'

@app.route(r'delete( task)? <task_num>')
def delete_task(task_num):
    task_num = int(task_num)
    del data[task_num]
    save(data)
    return f'ok i deleted task {task_num}'

@app.route(r'what should i do')
@app.route(r'what do i need to do')
def todo_list():
    return 'you should:\n{}'.format(print_tasks(sorted(query_data('task', state='do'), key=lambda d: d.get('context') or '')))

@app.route(r'what did i do')
def completed_list():
    return 'you did:\n{}'.format(print_tasks(sorted(query_data('task', state='done'), key=lambda d: d.get('updated') or datetime.datetime.now())))

@app.route(r'what am i waiting (on|for)')
@app.route(r'what are my agendas')
def waiting_list():
    return 'you are waiting for:\n{}'.format(print_tasks(query_data('task', state='waiting')))

@app.route(r'what is my agenda (for|with) <who>')
def waiting_list_who(who):
    return 'you\'re agenda with {}:\n{}'.format(who, print_tasks(query_data('task', who=who, state='waiting')))

@app.route(r'what should i maybe do')
@app.route(r'what is on my maybe list')
def todo_list():
    return 'you should maybe:\n{}'.format(print_tasks(query_data('task', state='maybe')))

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

@app.route(r'(task )?<task_num> is for <context>')
def set_context(task_num, context):
    task_num = int(task_num)
    task = data[task_num]
    task['context'] = context
    save(data)
    return 'got it. the context is set'

@app.route(r'what (do i need to|should i) do for <context>')
def set_context(context):
    return 'for {} you should:\n{}'.format(context, print_tasks(query_data('task', state='do', context=context)))

@app.route(r'<who> (should|needs to) do( task)? <task_num>')
@app.route(r'(i need|i\'m waiting for) <who> to do( task)? <task_num>')
def waiting_on_existing_task(who, task_num):
    task_num = int(task_num)
    task = data[task_num]
    task['who'] = who
    update_state(task, 'waiting')
    save(data)
    return f'got it. you are waiting for {who} to complete that task'

@app.route(r'<who> (should|needs to) <task_name>')
@app.route(r'(i need|i\'m waiting for) <who> to <task_name>')
def waiting(who, task_name):
    task = dict(type='task', name=task_name, who=who)
    update_state(task, 'waiting')
    data.append(task)
    save(data)
    return f'sure, i recorded this new task that you\'re waiting for. "{len(data) - 1}: {task_name}"'

@app.route(r'bye')
def bye():
    return 'bye'

@app.route(r'<any>')
def default(any):
    return 'ok... not really sure what you mean by that'
