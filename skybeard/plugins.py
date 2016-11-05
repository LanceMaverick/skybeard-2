import os
import sys
from telegram.ext import Updater
"""
Handles the loading and running of skybeard plugins.
architecture inspired by: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
and http://stackoverflow.com/a/17401329
"""

class PluginLoader(type):

    def __init__(cls, name, bases, attrs):
        if hasattr(cls, 'plugins'):
            cls.register(cls)
        else:
            cls.plugins = []

    def register(cls, plugin):
        instance = plugin()
        cls.plugins.append(instance)
        instance.initialise()

class Plugin(metaclass=PluginLoader):
    updater = Updater(os.environ.get('TG_BOT_TOKEN'))
    disp = updater.dispatcher
    updater.start_polling()

#to go in separate plugin module in plugins directory:
from telegram.ext import CommandHandler, MessageHandler, Filters, Job

#class EchoPlugin(Plugin):
#    def initialise(self):
#        self.disp.add_handler(CommandHandler("help", self.help))
#        self.disp.add_handler(MessageHandler(Filters.text, self.echo))
#        print('initialised')
#
#    def help(self, bot, update):
#        update.message.reply_text('Help!')
#
#    def echo(self, bot, update):
#        update.message.reply_text(update.message.text)
#
  
#show spacecats test plugin  
import random   
class PostCats(Plugin):
    
    def initialise(self):
        self.disp.add_handler(MessageHandler(Filters.text, self.listener))
    
    def listener(self, bot, update):
        message = update.message
        text = message.text
        if 'give me spacecats' in text or 'show me spacecats' in text:
            cat_photos= [
                    'http://i.imgur.com/bJ043fy.jpg',
                    'http://i.imgur.com/iFDXD5L.gif',
                    'http://i.imgur.com/6r3cMsl.gif',
                    'http://i.imgur.com/JpM5jcX.jpg',
                    'http://i.imgur.com/r7swEJv.jpg',
                    'http://i.imgur.com/vLVbiKu.jpg',
                    'http://i.imgur.com/Yy0TCXA.jpg',
                    'http://i.imgur.com/2eV7kmq.gif',
                    'http://i.imgur.com/rnA769W.jpg',
                    'http://i.imgur.com/08mxOAK.jpg'
                    ]

            i = random.randint(0, len(cat_photos)-1)
            
            try:
                update.message.reply_photo(photo=cat_photos[i])
            except Exception  as e:
                print(e)
                update.message.reply_photo(photo='http://cdn.meme.am/instances/500x/55452028.jpg')


