import os
import sys
from telegram.ext import Updater
"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""

class PluginLoader(type):

    def __init__(cls, name, bases, attrs):
        if hasattr(cls, 'plugins'):
            cls.register(cls)
        else:
            cls.plugins = []

    def register(cls, plugin):
        instance = plugin()
        cls.plugins.append(instance)
        instance.initialise()

class Plugin(metaclass=PluginLoader):
    updater = Updater(os.environ.get('TG_BOT_TOKEN'))
    disp = updater.dispatcher
    updater.start_polling()

#to go in separate plugin module in plugins directory:
from telegram.ext import CommandHandler, MessageHandler, Filters, Job

class EchoPlugin(Plugin):
    def initialise(self):
        self.disp.add_handler(CommandHandler("help", self.help))
        self.disp.add_handler(MessageHandler(Filters.text, self.echo))
        print('initialised')

    def help(self, bot, update):
        update.message.reply_text('Help!')

    def echo(self, bot, update):
        update.message.reply_text(update.message.text)
