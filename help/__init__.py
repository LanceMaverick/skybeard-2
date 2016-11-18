import re

import telepot

from skybeard.beards import BeardMixin

import config

def embolden(string):
    return "<b>"+string+"</b>"

def italisize(string):
    return "<i>"+string+"</i>"

async def fetch_user_help():
    """A little bit of magic to fetch all the __userhelp__'s."""
    retdict = dict()
    for beard in BeardMixin.beards:
        try:
            retdict[beard.__class__.__name__] = beard.__userhelp__
        except AttributeError:
            retdict[beard.__class__.__name__] = None

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This will make sense when this class inherits from BeardMixin
        self.register_command("help", self.send_help)

    _timeout = 2

    @property
    def __userhelp__(self):
        return "\n".join([
            "I'm the default help beard.",
            "",
            "/help - display the help for this bot."])

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
        # TODO update to something more proper
        await self.sender.sendMessage(retstr, parse_mode='html')


def create_help(config):

    class BeardedHelp(Help, BeardMixin):
        pass

    return BeardedHelp

