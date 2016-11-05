#show spacecats test plugin
import random

from skybeard.beards import Beard
from telegram.ext import MessageHandler, Filters

class PostCats(Beard):

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
