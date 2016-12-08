import telepot

# from skybeard.beards import BeardAsyncChatHandlerMixin
from skybeard.beards import BeardChatHandler, Beard, create_command

import config


def embolden(string):
    return "<b>"+string+"</b>"


def italisize(string):
    return "<i>"+string+"</i>"


async def fetch_user_help():
    """A little bit of magic to fetch all the __userhelp__'s."""
    retdict = dict()
    for beard in Beard.beards:
        name = beard.get_name()
        try:
            retdict[name] = beard.__userhelp__()
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


class Help(telepot.aio.helper.ChatHandler):

    @classmethod
    def __userhelp__(cls):
        return "\n".join([
            "I'm the default help beard.",
            "",
            "/help - display the help for this bot."])

    async def send_help(self, msg):
        retstr = ""
        try:
            try:
                retstr += config.__userhelp__
            except TypeError:
                retstr += config.__userhelp__()
        except AttributeError:
            retstr += ("My help message is unconfigured. To display "
                       "something here, add a docstring to my config.py.")

        userhelp = await fetch_user_help()
        userhelp = await format_user_help(userhelp)
        retstr += "\n\n{}".format(userhelp)
        await self.sender.sendMessage(retstr, parse_mode='html')


def create_help(config):

    class BeardedHelp(Help, BeardChatHandler):
        _timeout = 2
        __commands__ = [
            ('help', 'send_help', None),
        ]

    return BeardedHelp
