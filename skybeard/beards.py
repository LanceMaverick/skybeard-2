import os
import sys
from telegram.ext import Updater
"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""

class BeardLoader(type):
    def __init__(cls, name, bases, attrs):
        if hasattr(cls, 'beards'):
            cls.register(cls)
        else:
            cls.beards = []

    def register(cls, beard):
        instance = beard()
        cls.beards.append(instance)
        instance.initialise()

class Beard(metaclass=BeardLoader):
    updater = Updater(os.environ.get('TG_BOT_TOKEN'))
    disp = updater.dispatcher
    updater.start_polling()
    
    def error(self, bot, update, error):
        logger.warn('Update "{}" caused error "{}"'.format(update, error))

    # This is normally started in the main.py
    # updater.start_polling()

    def error(self, bot, update, error):
        logger.warn('Update "{}" caused error "{}"'.format(update, error))
