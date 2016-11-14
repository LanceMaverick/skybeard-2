import os
import textwrap

from telegram.ext import CommandHandler
from skybeard.beards import Beard

def is_module(filename):
    fname, ext = os.path.splitext(filename)
    if ext == ".py":
        return True
    elif os.path.exists(os.path.join(filename, "__init__.py")):
        return True
    else:
        return False

def get_literal_path(path_or_autoloader):
    try:
        return path_or_autoloader.path
    except AttributeError:
        assert type(path_or_autoloader) is str, "beard_path is not a str or an AutoLoader!"
        return path_or_autoloader

def get_literal_beard_paths(beard_paths):
    return [get_literal_path(x) for x in beard_paths]

def all_possible_beards(paths):
    literal_paths = get_literal_beard_paths(paths)

    for path in literal_paths:
        for f in os.listdir(path):
            if is_module(os.path.join(path, f)):
                yield os.path.basename(f)

def fetch_user_help():
    """A little bit of magic to fetch all the __userhelp__'s."""
    retdict = dict()
    for beard in Beard.beards:
        try:
            retdict[beard.__class__.__name__] = beard.__userhelp__
        except AttributeError:
            retdict[beard.__class__.__name__] = None

    return retdict

def embolden(string):
    return "<b>"+string+"</b>"

def italisize(string):
    return "<i>"+string+"</i>"

def format_user_help(userhelps):
    """Takes a dict of user help messages and formats them."""

    retstr = italisize("Start of beard documentation\n\n")
    for name, userhelp in sorted(userhelps.items(), key=lambda x: x[0]):
        if userhelp:
            retstr += "{name}:\n{userhelp}\n\n".format(name=embolden(name), userhelp=userhelp)
        else:
            retstr += "{name}:\nNo documentation found.\n\n".format(name=embolden(name))

    retstr += italisize("End of beard documentation.")

    return retstr


def create_help(config):
    class Help(Beard):
        def initialise(self):
            self.disp.add_handler(CommandHandler('help', self.send_help))

        @property
        def __userhelp__(self):
            return "\n".join([
                "I'm the default help beard.",
                "",
                "/help - display the help for this bot."])

        def send_help(self, bot, update):
            if config.__doc__:
                update.message.reply_text(config.__doc__)
            else:
                update.message.reply_text(
                    ("My help message is unconfigured. To display "
                    "something here, add a docstring to my config.py."))

            # TODO update to something more proper
            update.message.reply_text("By the way:\n\n{}".format(format_user_help(fetch_user_help())),
                                      parse_mode='html',
                                      quote=False)

    return Help
