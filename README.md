# hey
Conversational life management in the terminal

# Example Session
```
$ hey i should buy milk
sure, you now have a task "0: buy milk"

$ hey what should i do
you should:
  id  name      state    context    who    updated     link
----  --------  -------  ---------  -----  ----------  ------
   0  buy milk  do                         2022-12-24

$ hey i should respond to an email
sure, you now have a task "1: respond to an email"

$ hey the link for 1 is https://mail.google.com/3837289738764
got it. the link is updated

$ hey open the link for 1
ok

$ hey what should i do
you should:
  id  name                 state    context    who    updated     link
----  -------------------  -------  ---------  -----  ----------  ---------------
   0  buy milk             do                         2022-12-24
   1  respond to an email  do                         2022-12-24  mail.google.com

$ hey i did 0
good job! i checked off task "buy milk"

$ hey what should i do
you should:
  id  name                 state    context    who    updated     link
----  -------------------  -------  ---------  -----  ----------  ---------------
   1  respond to an email  do                         2022-12-24  mail.google.com

$ hey what did i do
you did:
  id  name      state    context    who    updated     link
----  --------  -------  ---------  -----  ----------  ------
   0  buy milk  done                       2022-12-24
```

# Make a virtual environment

```
mkvirtualenv hey
```

# Install hey

```
pip install -e .
```

# Set these enviroment variables to use jsonbin instead of a JSON file

```
export HEY_JSONBIN_KEY='<key>'
export HEY_JSONBIN_ID='<id>'
```
