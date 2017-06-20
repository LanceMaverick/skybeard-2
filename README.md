# skybeard v2.0

![Skybeard](http://i.imgur.com/BkjfI3k.png)

A plug-in based telegram bot

## Installation
It is recommended to use a `virtualenv` for Skybeard. Create and activate the virtual environment with
```
virtualenv venv
source venv/bin/activate
```
then install the base requirements with
```
pip install -r requirements.txt
```

You will then need to make a `config.py`. An example `config.py` is provided so you can simply:
```
cp config.py.example config.py
```

## Installation with docker
This method is currently in beta. It requires docker-compose.

```
cp docker-compose.yml.example docker-compose.yml
```
then replace `YOUR_TOKEN_GOES_HERE` in `docker-compose.yml` with your token. Then run

```
docker-compose up --build
```

And skybeard will be (hopefully) running!

## Running Skybeard

To run skybeard define your key in the environment variable `$TG_BOT_TOKEN` or as an argument with `-k` and run `main.py`. this can be done easily e.g.:

    ./main.py -k 99121185:RUE-ObViouSlyFakeKeyTHaThaSbEEnmad 

## Testing skybeard
To test that your skybeard is running out of the box, use the test config like so:

    ./main.py -k 99121185:RUE-ObViouSlyFakeKeyTHaThaSbEEnmadEuP -c config.tests.yml
    
and type `/help` to see the commands available.

## Skybeard's many beards
Skybeard source documentation: http://skybeard-2.readthedocs.io/en/latest/

Skybeard wears many beards. The bot will automatically load any "beard" (a plug-in) that is placed in the beards folder. Beards are typically structured like so:

```
beards
|
|___my_beard
    |    config.yml
    |    requirements.txt
    |    setup_beard.py
    |___python
        |___my_beard
            |   __init__.py
    |
    |___docs
        |    README
        |    ...
```

In this example the `myBeard` folder containts a `requirements.txt` for any additonal dependencies so they can be pipped, a `config.py` file for configuration of the beard and settings and the `__init__.py` which contains the class that that is the interface between the plug-in and skybeard. 
This interface class inherits from `skybeard.beards.BeardChatHandler` which handles the mounting of the plug-in, registering of commands etc, and also the `telepot.aio.helper.ChatHandler`. 

The folder can also contain any other python modules and files that are needed for the plugin.

## Growing a new beard
Creating a new beard requires knowledge of the **telepot** telegram API, see: http://telepot.readthedocs.io/en/latest/

The quickest way to make a new beard is to use the utility script `utils/newbeard.py` which creates the folder structure and basic files.

```
$ utils/newbeard.py foo_beard
$ tree foo_beard
foo_beard
├── python
│   └── foo_beard
│       └── __init__.py
├── README.txt
└── setup_beard.py

2 directories, 3 files
```

The main part of the code is in `python/beard_name/__init__.py`.

An example async plug-in that would echo the user's message would look like this:


```Python
class Echo(BeardChatHandler):

    __userhelp__ = """A simple echo beard. Echos whatever it is sent."""
 
    __commands__ = [
        #(condition/command, callback coro, help text)
        (Filters.text, 'echo', 'Echos everything said by anyone.'),
        ('hello', 'say_hello', 'Greets the user'),
    ]

    async def echo(self, msg):
        await self.sender.sendMessage(msg['text'])

    async def say_hello(self, msg):
        name = msg['from']['first_name']
        await self.sender.sendMessage('Hello {}!'.format(name))

```
This plug-in will greet the user when they send "/hello" to Skybeard  and will also echo back any text the user sends.

`__userhelp__` is a brief string used to generate the bot's help message.
`__commands__` is a list of tuples. the 0th element of each tuple gives a condition, such as a filter, or a command string (without the slash). The 1st element is the function that is called when the condition is met, and the 2nd element is the help text which, along with `__userhelp__` is used to generate the help message (such as when the user types "/help").


See the examples folder for examples of callback functionality, timers, and regex predication. 
