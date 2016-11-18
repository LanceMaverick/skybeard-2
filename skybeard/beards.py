import re
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
        cls.beards.append(beard)


def command_predicate(cmd):
    return lambda x: re.match(r"/{}(?:@\w+)?".format(cmd), x['text'])

class BeardMixin(metaclass=BeardLoader):
    # Default timeout for Beards
    _timeout = 10
    _all_commands = []

    def __init__(self, *args, **kwargs):
        self._commands = []

    @classmethod
    def setup_beards(cls, key):
        cls.key = key

    @classmethod
    def _register_command_with_class(cls, cmd):
        cls._all_commands.append(cmd)

    def register_command(self, cmd, coro):
        self._register_command_with_class(cmd)
        self._commands.append((command_predicate(cmd), coro))

    async def on_chat_message(self, msg):
        for predicate, coro in self._commands:
            if predicate(msg):
                await coro(msg)
