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
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler


class EchoPlugin(BeardChatHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #register command "/hello" to dispatch to self.say_hello()
        self.register_command("hello", self.say_hello)
    
    #is called when "/hello" is sent
    async def say_hello(self, msg):
        name = msg['from']['first_name']
        await self.sender.sendMessage('Hello {}!'.format(name))
    
    #is called every time a message is sent
    async def on_chat_message(self, msg):
        text = msg['text']
        await self.sender.sendMessage(text)
        await super().on_chat_message(msg)
```

This plug-in will greet the user when they send "/hello" to Skybeard by using the `register_command()` method of the `BeardChatHandler` and will also echo back any text the user sends by overwriting the `on_chat_message()` method (and calling the base method with `super()` afterwards).

See the examples folder for examples of callback functionality, timers, and regex predication. 


