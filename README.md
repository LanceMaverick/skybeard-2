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

## Running Skybeard

To run skybeard define your key in the environment variable `$TG_BOT_TOKEN` or as an argument with `-k` and run `main.py`. this can be done easily e.g.:

    ./main.py -k 99121185:RUE-UAa7dsEaagAKkysPDjqa2X7KxX48e 

## Skybeard's many beards
Skybeard source documentation: http://skybeard-2.readthedocs.io/en/latest/
Skybeard wears many beards. The bot will automatically load any "beard" (a plug-in) that is placed in the beards folder. Beards are typically structured like so:

```
beards
|
|___myBeard
    |    __init__.py
    |    config.py
    |    requirements.txt
    |    ...
    |
    |___docs
        |    README
        |    ...
```

In this example the `myBeard` folder containts a `requirements.txt` for any additonal dependencies so they can be pipped, a `config.py` file for configuration of the beard and settings and the `__init__.py` which contains the class that that is the interface between the plug-in and skybeard. 
This interface class inherits from skybeard.beards.BeardChatHandler` which handles the mounting of the plug-in, registering of commands etc, and also the `telepot.aio.helper.ChatHandler`. 

The folder can also contain any other python modules and files that are needed for the plugin.

## Growing a new beard
Creating a new beard requires knowledge of the **telepot** telegram API, see: http://telepot.readthedocs.io/en/latest/

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
