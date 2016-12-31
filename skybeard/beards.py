"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""
import re
import logging
import json
import telepot.aio

logger = logging.getLogger(__name__)


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


# TODO rename coro to coro_name or something better than that

class Command(object):
    def __init__(self, pred, coro, hlp=None):
        self.pred = pred
        self.coro = coro
        self.hlp = hlp


class SlashCommand(object):
    def __init__(self, cmd, coro, hlp=None):
        self.cmd = cmd
        self.pred = command_predicate(cmd)
        self.coro = coro
        self.hlp = hlp


def create_command(cmd_or_pred, coro, hlp=None):
    if isinstance(cmd_or_pred, str):
        return SlashCommand(cmd_or_pred, coro, hlp)
    elif callable(cmd_or_pred):
        return Command(cmd_or_pred, coro, hlp)
    raise TypeError("cmd_or_pred must be str or callable.")


class Beard(type):
    beards = list()

    def __new__(mcs, name, bases, dct):
        if "__userhelp__" not in dct:
            dct["__userhelp__"] = ("The author has not defined a "
                                   "<code>__userhelp__</code> for this beard.")

        if "__commands__" in dct:
            for i in range(len(dct["__commands__"])):
                tmp = dct["__commands__"].pop(0)
                dct["__commands__"].append(create_command(*tmp))

        return type.__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, attrs):
        # If specified as base beard, do not add to list
        try:
            if attrs["__is_base_beard__"] is False:
                Beard.beards.append(cls)
        except KeyError:
            attrs["__is_base_beard__"] = False
            Beard.beards.append(cls)

        super().__init__(name, bases, attrs)

    def register(cls, beard):
        cls.beards.append(beard)


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
    __is_base_beard__ = True

    _timeout = 10

    def __init__(self, *args, **kwargs):
        self._instance_commands = []
        super().__init__(*args, **kwargs)

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

    def register_command(self, pred_or_cmd, coro, hlp=None):
        logging.debug("Registering instance command: {}".format(pred_or_cmd))
        self._instance_commands.append(create_command(pred_or_cmd, coro, hlp))

    @classmethod
    def get_name(cls):
        return cls.__name__

    async def on_chat_message(self, msg):
        try:
            for cmd in type(self).__commands__:
                if cmd.pred(msg):
                    await getattr(self, cmd.coro)(msg)
        except AttributeError:
            # No __commands__ in bot? pass
            pass

        for cmd in self._instance_commands:
            if cmd.pred(msg):
                if callable(cmd.coro):
                    await cmd.coro(msg)
                else:
                    await getattr(self, cmd.coro)(msg)
