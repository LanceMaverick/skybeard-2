"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""
import re
import logging
import json
import telepot.aio
from copy import deepcopy

logger = logging.getLogger(__name__)


# This is a metaclass. Let's do this thing.
class Beard(type):
    beards = list()

    def __new__(mcs, name, bases, dct):
        # If there is a __userhelp__ present and it's an ordinary string, make
        # it a function that returns that string
        if "__userhelp__" in dct:
            if isinstance(dct["__userhelp__"], str):
                tmp = dct["__userhelp__"]
                mcs.__userhelp__ = classmethod(lambda x: tmp)
                dct["__userhelp__"] = mcs.__userhelp__

        return type.__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, attrs):
        if not ("__is_base_beard__" in attrs and
                attrs["__is_base_beard__"] == True):
            Beard.beards.append(cls)
        super().__init__(name, bases, attrs)

    def register(cls, beard):
        cls.beards.append(beard)


def regex_predicate(pattern):
    def retfunc(msg):
        try:
            logging.debug("Matching regex: '{}'".format(pattern))
            retmatch = re.match(pattern, msg['text'])
            logging.debug("Match: {}".format(retmatch))
            return retmatch
        except KeyError:
            return False

    return retfunc


def command_predicate(cmd):
    return regex_predicate(r"^/{}(?:@\w+)?".format(cmd))


class Filters:
    @classmethod
    def text(cls, msg):
        return "text" in msg

    @classmethod
    def document(cls, msg):
        return "document" in msg

    @classmethod
    def location(cls, msg):
        return "location" in msg


class ThatsNotMineException(Exception):
    pass


class BeardChatHandler(telepot.aio.helper.ChatHandler, metaclass=Beard):
    # Default timeout for Beards

    __is_base_beard__ = True

    _timeout = 10
    _all_commands = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._commands = []

    def _make_uid(self):
        return type(self).__name__+str(self.chat_id)

    def serialize(self, data):
        return json.dumps((self._make_uid(), data))

    def deserialize(self, data):
        data = json.loads(data)
        if data[0] == self._make_uid():
            return data[1]
        else:
            raise ThatsNotMineException(
                "Data does not belong to this bot!")

    @classmethod
    def setup_beards(cls, key):
        cls.key = key

    @classmethod
    def _register_command_with_class(cls, cmd):
            cls._all_commands.append(cmd)

    @classmethod
    def get_name(cls):
        return cls.__name__

    def register_command(self, cmd, coro):
        self._register_command_with_class(cmd)
        try:
            if callable(cmd):
                logger.debug("Registering coroutine: {}.".format(cmd))
                self._commands.append((cmd, coro))
            elif type(cmd) is str:
                logger.debug("Registering command: {}.".format("/"+cmd))
                self._commands.append((command_predicate(cmd), coro))
            else:
                raise TypeError(
                    "register_command requires either str or callable.")
        except AttributeError as e:
            logger.error(("Class not initialised properly. "
                          "Did you do super().__init__(*args, **kwargs)?"))
            raise e

    async def on_chat_message(self, msg):
        for predicate, coro in self._commands:
            if predicate(msg):
                await coro(msg)
