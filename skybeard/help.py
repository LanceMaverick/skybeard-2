import telepot

# from skybeard.beards import BeardAsyncChatHandlerMixin
from skybeard.beards import BeardChatHandler, Beard, SlashCommand
from skybeard.mixins import PaginatorMixin
from skybeard.utils import embolden, italisize

# import config
import pyconfig
import yaml



# TODO neaten the logic so fetching and formatting are truly separate again
async def fetch_user_help():
    """Returns a dictionary of all the __userhelp__'s defined in the loaded
    plug-ins."""
    retdict = dict()
    for beard in Beard.beards:
        name = beard.get_name()
        try:
            retdict[name] = beard.__userhelp__
            if hasattr(beard, '__commands__'):
                retdict[name] += "\n\n"
                for cmd in beard.__commands__:
                    if isinstance(cmd, SlashCommand):
                        retdict[name] += "/{} - {}\n".format(
                            cmd.cmd, cmd.hlp)
        except AttributeError:
            retdict[name] = None

    return retdict


async def format_user_help(name, userhelp):
    """Takes a dict of user help messages and formats them."""

    retstr = ""
    if userhelp:
        retstr += "{name}:\n{userhelp}\n\n".format(name=embolden(name), userhelp=userhelp)
    else:
        retstr += "{name}:\nNo documentation found.\n\n".format(name=embolden(name))

    return retstr


async def format_user_helps(userhelps):
    """Takes a dict of user help messages and formats them."""

    retstr = italisize("List of beard documentation:\n\n")
    for name, userhelp in sorted(userhelps.items(), key=lambda x: x[0]):
        retstr += await format_user_help(name, userhelp)

    retstr += italisize("End of beard documentation.")

    return retstr


async def format_user_helps_paginated(userhelps):
    """Takes a dict of user help messages and formats them."""

    retlist = []
    for name, userhelp in sorted(userhelps.items(), key=lambda x: x[0]):
        retstr = italisize("Beard documentation:\n\n")
        retstr += await format_user_help(name, userhelp)
        # retstr += italisize("End of beard documentation.")

        retlist.append(retstr)

    return retlist


def get_all_cmd_helps():
    """Retrieves the help messages in the tuples of each plug-in's
    __commands__ list"""
    all_cmds = set()
    for beard in Beard.beards:
        for cmd in beard.__commands__:
            if isinstance(cmd, SlashCommand):
                all_cmds.add(cmd)
    str_list = ["{} - {}".format(x.cmd, x.hlp) for x in all_cmds]
    return "\n".join(str_list)


# TODO clean up this function!
def create_help():
    config = yaml.load(open(pyconfig.get('config_file')))

    class Help(telepot.aio.helper.ChatHandler):

        async def send_help(self, msg):
            """sends the user a combined help message for all plug-ins"""
            retstr = ""
            try:
                retstr += config.__userhelp__
            except AttributeError:
                retstr += ("My help message is unconfigured. To display "
                        "something here, add a docstring to my config.py.")

            userhelps = await fetch_user_help()
            userhelps = await format_user_helps(userhelps)
            retstr += "\n\n{}".format(userhelps)
            await self.sender.sendMessage(retstr, parse_mode='html')

        async def send_paginated_help(self, msg):
            """sends the user a combined help message for all plug-ins"""
            retstr = ""
            try:
                retstr += config.__userhelp__
            except AttributeError:
                retstr += ("My help message is unconfigured. To display "
                        "something here, add a docstring to my config.py.")

            userhelps = await fetch_user_help()
            userhelps = await format_user_helps_paginated(userhelps)

            async def identity(x):
                return x

            await self.send_paginated_message(userhelps, identity)
            # retstr += "\n\n{}".format(userhelps)
            # await self.sender.sendMessage(retstr, parse_mode='html')

        async def cmd_helps(self, msg):
            """sends the user a formatted list of commands for easy registering with
            botfather"""
            await self.sender.sendMessage(
                "Forward the following to the BotFather when he asks for your "
                "list of commands.")
            await self.sender.sendMessage(get_all_cmd_helps(), parse_mode="HTML")

    class BeardedHelp(Help, PaginatorMixin, BeardChatHandler):
        """Beard for interfacing help functionality with telegram"""
        _timeout = 2
        __commands__ = [
            ('help', 'send_help', "Shows verbose help message."),
            ('helppaged', 'send_paginated_help', "Shows verbose help message, paginated."),
            ('cmdhelps', 'cmd_helps', "Lists all commands available."),
        ]

        __userhelp__ = "I'm the default help beard."

    return BeardedHelp
