from telegram.ext import CommandHandler
from skybeard.beards import Beard

def create_help(config):
    class Help(Beard):
        def initialise(self):
            self.disp.add_handler(CommandHandler('help', self.send_help))

        def send_help(self, bot, update):
            if config.__doc__:
                update.message.reply_text(config.__doc__)
            else:
                update.message.reply_text(
                    ("My help message is unconfigured. To display "
                    "something here, add a docstring to my config.py."))

    return Help
