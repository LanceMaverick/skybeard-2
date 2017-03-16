"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""
import asyncio
import logging
import json
import traceback

import telepot.aio
import pyconfig

from .bearddbtable import BeardDBTable
from .logging import TelegramHandler
from .predicates import command_predicate
# from skybeard.server import async_post, async_get, web
from skybeard.server import app
from aiohttp import web

logger = logging.getLogger(__name__)


# TODO rename coro to coro_name or something better than that


class Command(object):
    """Holds information to determine whether a function should be triggered."""
    def __init__(self, pred, coro, hlp=None):
        self.pred = pred
        self.coro = coro
        self.hlp = hlp

    def toJSON(self):
        try:
            return {
                "predicate": self.pred.toJSON(),
                "help": self.hlp,
            }
        except AttributeError:
            return {
                "predicate": "(unserializable)",
                "help": self.hlp,
            }


class SlashCommand(object):
    """Holds information to determine whether a telegram command was sent."""
    def __init__(self, cmd, coro, hlp=None):
        self.cmd = cmd
        self.pred = command_predicate(cmd)
        self.coro = coro
        self.hlp = hlp

    def toJSON(self):
        return {
            "command": "/"+self.cmd,
            "help": self.hlp
        }

def create_command(cmd_or_pred, coro, hlp=None):
    """Creates a Command or SlashCommand object as appropriate.

    Used to make __commands__ tuples into Command objects."""
    if isinstance(cmd_or_pred, str):
        return SlashCommand(cmd_or_pred, coro, hlp)
    elif callable(cmd_or_pred):
        return Command(cmd_or_pred, coro, hlp)
    raise TypeError("cmd_or_pred must be str or callable.")

# def create_route(route, coro, method):
#     """creates an endpoint for the web server"""
#     if method.lower() == 'post':
#         @async_post(route)
#         def handler(request):
#             return coro(request)
#     elif method.lower() == 'get':
#         @async_get(route)
#         def handler(request):
#             return coro(request)
#     else:
#         raise ValueError('HTTP method "{}" not supported'.format(method))


class Beard(type):
    """Metaclass for creating beards."""

    beards = list()

    def __new__(mcs, name, bases, dct):
        if "__userhelp__" not in dct:
            dct["__userhelp__"] = ("The author has not defined a "
                                   "<code>__userhelp__</code> for this beard.")

        if "__commands__" in dct:
            for i in range(len(dct["__commands__"])):
                tmp = dct["__commands__"].pop(0)
                dct["__commands__"].append(create_command(*tmp))

        if "__routes__" in dct:
            for r in dct["__routes__"]:
                endpoint = r[1]
                if isinstance(r[2], str):
                    methods = (r[2],)
                else:
                    methods = r[2]
                fn_to_route = getattr(mcs, r[1])

                app.add_route(fn_to_route, endpoint=endpoint, methods=methods)

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
        """Add beard to internal list of beards."""
        cls.beards.append(beard)


class ThatsNotMineException(Exception):
    """Raised if data does not match beard.

    Used to check if serialized callback data belongs to the plugin. See
    BeardChatHandler.serialize()"""
    pass


class BeardChatHandler(telepot.aio.helper.ChatHandler, metaclass=Beard):
    """Chat handler for beards.

    This is the primary interface between skybeard and any plug-in. The plug-in
    must define a class that inherets from BeardChatHandler.

    This class should overwrite __commands__ with a list of tuples that route
    messages containing commands, or if they pass certain "Filters"
    (see skybeard.beards.Filters).
    E.g:

    ```Python
    __commands__ = [
            ('mycommand', 'my_func', 'this is a help message'),
            (Filters.location, 'my_other_func', 'another help message')]
    ```

    In this case, when the bot receives the command "/mycommand", it will call
    self.my_func(msg) where msg is a dict containing all the message
    information. The filter (from skybeard.beards) will call
    self.my_other_func(msg) whenever "msg" contains a location. The help
    messages are collected by the help functions and automatically formatted
    and sent when a user sends /help to the bot.

    Instances of the plug-in classes are created when required (such as when
    a filter is passed, a command or a regex pattern for the bot is matched
    etc.) and they are destructed after a set timeout. The default is 10
    seconds, but this can be overwritten with, for example

    _timeout = 90

    The class should also define a __userhelp__ string which will be
    used in the auto help message generation.
    """
    __is_base_beard__ = True

    _timeout = 10

    __commands__ = []

    # Should be got with get_username.
    #
    # TODO find a way to use coroutines as property getters and setters
    _username = None

    async def get_username(self):
        """Returns the username of the bot"""
        if type(self)._username is None:
            type(self)._username = (await self.bot.getMe())['username']

        return type(self)._username

    @classmethod
    def toJSON(cls):
        # Not a coroutine because it's useful to use this in list
        # comprehensions
        return {
            "name": cls.__name__,
            "commands": [c.toJSON() for c in cls.__commands__],
            "userhelp": cls.__userhelp__
        }

    def __init__(self, *args, **kwargs):
        self._instance_commands = []
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(
            "beardlogger.{}.{}".format(self.get_name(), self.chat_id))
        self._handler = TelegramHandler(self)
        self.logger.addHandler(self._handler)

    def create_db_table(self, table_name, **kwargs):
        """Creates `BeardDBTable` using current beard.

        Note that this does not create a table in the database. Tables are only
        created once the `BeardDBTable` is used with `with`.

        """
        return BeardDBTable(self, table_name, **kwargs)

    def on_close(self, e):
        """Removes per beard logger handler and calls telepot default on_close."""
        self.logger.removeHandler(self._handler)
        super().on_close(e)

    async def __onerror__(self, e):
        """Runs when functions decorated with @onerror except.

        Useful for emitting debug crash logs. Can be overridden to use custom
        error tracking (e.g. telegramming the author of the beard when a crash
        happens.)

        """
        self.logger.debug(
            "More details on crash of {}:\n\n{}".format(
                self,
                "".join(traceback.format_tb(e.__traceback__))))

    def _make_uid(self):
        """Generates a unique ID for the beard which is
        different for each chat"""
        return type(self).__name__+str(self.chat_id)

    def serialize(self, data):
        """Serialises data to be specific for each beard instance.

        Serialize callback data (such as with inline keyboard buttons). The id
        of the plug-in is encoded into the callback data so ownership of
        callbacks can be easily checked when it is deserialized. Also avoids
        the same plug-in receiving callback data from another chat

        """
        return json.dumps((self._make_uid(), data))

    def deserialize(self, data):
        """Deserializes the callback data"""
        data = json.loads(data)
        if data[0] == self._make_uid():
            return data[1]
        else:
            raise ThatsNotMineException(
                "Data does not belong to this bot!")

    @classmethod
    def setup_beards(cls, key, db_url):
        """Perform setup necessary for all beards."""
        pyconfig.set('key', key)
        pyconfig.set('db_url', db_url)
        cls.key = key
        cls.db_url = db_url

    def register_command(self, pred_or_cmd, coro, hlp=None):
        """Registers an instance level command.

        This can be used to create instance specific commands e.g. if a user
        needs to type /cmdSOMEAPIKEY:

        ```
        self.register_commmand('cmd{}'.format(SOMEAPIKEY), 'name_of_coro')
        ```
        """

        logging.debug("Registering instance command: {}".format(pred_or_cmd))
        self._instance_commands.append(create_command(pred_or_cmd, coro, hlp))

    @classmethod
    def get_name(cls):
        """Get the name of the beard (e.g. cls.__name__)."""
        return cls.__name__

    async def on_chat_message(self, msg):
        """Default on_chat_message for beards.

        Can be overwritten in order to define the behaviour of the plug-in
        whenever any message is received.

        NOTE: super().on_chat_message(msg) must be called in the overwrite to
        preserve default behaviour. This is usually done after custom
        behaviour, e.g.

        ```Python
        async def on_chat_message(self, msg):
            await self.sender.sendMessage("I got your message!")

            super().on_chat_message(msg)
        ```

        """
        for cmd in self._instance_commands + type(self).__commands__:
            if asyncio.iscoroutinefunction(cmd.pred):
                pred_value = await cmd.pred(self, msg)
            else:
                pred_value = cmd.pred(self, msg)
            if pred_value:
                if asyncio.iscoroutinefunction(cmd.coro):
                    await cmd.coro(msg)
                elif callable(cmd.coro):
                    cmd.coro(msg)
                else:
                    await getattr(self, cmd.coro)(msg)


@app.add_route('/loadedBeards', methods=['GET'])
async def loaded_beards(request):
    return web.json_response([b.toJSON() for b in Beard.beards])


@app.add_route('/availableCommands', methods=['GET'])
async def available_commands(request):
    d = {}
    for beard in Beard.beards:
        cmds = []
        for cmd in beard.__commands__:
            if isinstance(cmd, SlashCommand):
                cmds.append(dict(command=cmd.cmd, hint=cmd.hlp))
        if cmds:
            d[beard.__name__] = cmds

    return web.json_response(d)
