#show spacecats test plugin
# Adapted from work by LanceMaverick
import random
import logging
from urllib.request import urlopen

import telepot
import telepot.aio

from skybeard.beards import BeardAsyncChatHandlerMixin, regex_predicate

class PostCats(telepot.aio.helper.ChatHandler, BeardAsyncChatHandlerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command(
            regex_predicate('(give|show) me spacecats'), self.send_cat)

    async def send_cat(self, msg):
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

        try:
            await self.sender.sendPhoto(("cat_photo.jpg", urlopen(random.choice(cat_photos))))
        except Exception as e:
            logging.error(e)
            await self.sender.sendPhoto(
                ("cat_photo.jpg",
                 urlopen('http://cdn.meme.am/instances/500x/55452028.jpg')))
