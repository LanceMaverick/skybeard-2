from plugins import Plugin
from telegram.ext import CommandHandler, MessageHandler, Filters, Job

class EchoPlugin(Plugin):
    def initialise(self):
        self.disp.add_handler(CommandHandler("help", self.help))
        self.disp.add_handler(MessageHandler(Filters.text, self.echo))
        print('initialised')

    def help(self, bot, update):
        update.message.reply_text('Help!')

    def echo(self, bot, update):
        update.message.reply_text(update.message.text)
        
