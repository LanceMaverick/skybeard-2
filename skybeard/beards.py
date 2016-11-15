import os
import sys
from telegram.ext import Updater
"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""

import logging
logger = logging.getLogger(__name__)


class BeardLoader(type):
    def __init__(cls, name, bases, attrs):
        if hasattr(cls, 'beards'):
            cls.register(cls)
        else:
            cls.beards = []

    def register(cls, beard):
        # instance = beard()
        # cls.beards.append(instance)
        # instance.initialise()
        cls.beards.append(beard)


class Beard(metaclass=BeardLoader):
    @classmethod
    def setup_beard(cls, key):
        cls.updater = Updater(key)
        cls.disp = cls.updater.dispatcher

    def error(self, bot, update, error):
        logger.warn('Update "{}" caused error "{}"'.format(update, error))

    # This is normally started in the main.py
    # updater.start_polling()

class BeardMixin(metaclass=BeardLoader):
    # Default timeout for Beards
    _timeout = 10

    @classmethod
    def setup_beards(cls, key):
        cls.key = key
