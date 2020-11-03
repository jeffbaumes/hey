import sys

from commands import app

def cli():
    command = ' '.join(sys.argv[1:])
    if len(command) > 0:
        print(app.serve(command))
        return
    print('sup')
    while True:
        command = input('>>>> ')
        response = app.serve(command)
        print(response)
        if response == 'bye':
            break
