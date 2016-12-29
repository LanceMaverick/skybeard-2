import telepot

# from skybeard.beards import BeardAsyncChatHandlerMixin
from skybeard.beards import BeardChatHandler, Beard, SlashCommand

import config


def embolden(string):
    return "<b>"+string+"</b>"


def italisize(string):
    return "<i>"+string+"</i>"


# TODO neaten the logic so fetching and formatting are truly separate again
async def fetch_user_help():
    """A little bit of magic to fetch all the __userhelp__'s."""
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


async def format_user_help(userhelps):
    """Takes a dict of user help messages and formats them."""

    retstr = italisize("List of beard documentation:\n\n")
    for name, userhelp in sorted(userhelps.items(), key=lambda x: x[0]):
        if userhelp:
            retstr += "{name}:\n{userhelp}\n\n".format(name=embolden(name), userhelp=userhelp)
        else:
            retstr += "{name}:\nNo documentation found.\n\n".format(name=embolden(name))

    retstr += italisize("End of beard documentation.")

    return retstr


def get_all_cmd_helps():
    all_cmds = set()
    for beard in Beard.beards:
        for cmd in beard.__commands__:
            if isinstance(cmd, SlashCommand):
                all_cmds.add(cmd)
    str_list = ["{} - {}".format(x.cmd, x.hlp) for x in all_cmds]
    return "\n".join(str_list)


class Help(telepot.aio.helper.ChatHandler):

    async def send_help(self, msg):
        retstr = ""
        try:
            retstr += config.__userhelp__
        except AttributeError:
            retstr += ("My help message is unconfigured. To display "
                       "something here, add a docstring to my config.py.")

        userhelp = await fetch_user_help()
        userhelp = await format_user_help(userhelp)
        retstr += "\n\n{}".format(userhelp)
        await self.sender.sendMessage(retstr, parse_mode='html')

    async def cmd_helps(self, msg):
        await self.sender.sendMessage(
            "Forward the following to the BotFather when he asks for your "
            "list of commands.")
        await self.sender.sendMessage(get_all_cmd_helps())


def create_help(config):

    class BeardedHelp(Help, BeardChatHandler):
        _timeout = 2
        __commands__ = [
            ('help', 'send_help', "Shows verbose help message."),
            ('cmdhelps', 'cmd_helps', "Lists all commands available."),
        ]

        __userhelp__ = "I'm the default help beard."

    return BeardedHelp
