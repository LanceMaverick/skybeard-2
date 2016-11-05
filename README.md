# skybeard v2.0

![Skybeard](http://i.imgur.com/fb2r696.jpg)

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

## Running Skybeard

To run skybeard define your key in the environment variable `$TG_BOT_TOKEN` and run `main.py`. this can be done easily e.g.:

    TG_BOT_TOKEN=99121185:RUE-UAa7dsEaagAKkysPDjqa2X7KxX48e ./main.py

## Skybeard's many beards
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

The `myBeard` folder containts a `requirements.txt` for any additonal dependencies so they can be pipped, a `config.py` file for user specific variables (e.g private API keys) and settings and the `__init__.py` which contains the class that must inheret from `beards.Beard`.
The folder can also contain any other python modules and files that are needed for the plugin, but Skybeard interfaces only with the `Beard` class in `__init.py__`, allowing you to separate out the beard's logic from the interface.

## Growing a new beard
Creating a new beard requires knowledge of the python-telegram-bot API, see: https://github.com/python-telegram-bot/python-telegram-bot#documentation.
The minimum requirement for a working beard is a plug-in class in the `__init__.py` of your beard's folder, which inherits from `beards.beard`. In this class, the telegram `Updater` and `Dispatcher` can be interfaced with (via `self.updater` and `self.disp` respectively). The beard must define an `initialise()` method that registers any handlers with the bot. 
For example a simple echo plug-in, that echo's a user's message would look like this:
```
from skybeard.beards import Beard
from telegram.ext import MessageHandler, Filters

class EchoPlugin(Beard):
    
    def initialise(self):
        self.disp.add_handler(CommandHandler("help", self.help))
        self.disp.add_handler(MessageHandler(Filters.text, self.echo))

    def help(self, bot, update):
        update.message.reply_text('I echo your messages')

    def echo(self, bot, update):
        update.message.reply_text(update.message.text)
```
The interfacing with the python-telegram-bot API is no different to the echobot example supplied by python-telegram-bot:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
The key differences being that any handlers and listeners are added to the dispatcher in the parent `Beard` class.

### Structure and style
For large and complex plug-ins, most logic should be kept out of the `Beard` class. When adding command handlers, they can callback to, for instance, a function in a private module within the plug-in. 
For message handlers, or anything that requires some form of processing of the input, it is bes to do this within the '`Beard` class before calling the approriate functions. For instance, in the weather plug-in, the plug-in is called with the `/weather` command, but this gives the weather for a default location specified in the `config.py`, unless a location is given as an argument to this command. E.g. `/weather Dublin, Ireland`. The input is interpreted in the `Weather` class in `__init__.py` before calling the function in `forecast()` function in `weather.py` with the relevant arguments:

In `__init.py__`:
```
class Weather(Beard):
    
    #register the command /weather, which will callback to self.forecast
    def initialise(self):
        self.disp.add_handler(CommandHandler('weather', self.forecast))
    
    #forecast interprets th input before weather.forecast() does all the work
    def forecast(self, bot, update): 
        location = update.message.text.split('/weather',1)[1]
        if not location:
            location = config.default_location
        weather.forecast(bot, update) 
```
Separating the two like this ensures command and message handling can be modified easily, such as with adding new features or avoiding conflicts with other plug-ins.


