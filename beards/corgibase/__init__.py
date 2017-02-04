#show spacecats test plugin
# Adapted from work by LanceMaverick
import random
import logging
from urllib.request import urlopen
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate

class CorgiBase(BeardChatHandler):
    __userhelp__ = """
    Say give me corgis or show me corgis to see some corgis!"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command(
            regex_predicate('(give|show) me corgis'), self.send_corgi)

    async def send_corgi(self, msg):
        corgi_photos= [
                'http://i.imgur.com/vE7TLA2.jpg',
		'https://i.imgur.com/v0ZzD8O.jpg',
		'http://i.imgur.com/XBNueYD.jpg',
		'http://i.imgur.com/ATa8cDd.jpg',
                ]

        try:
            choice = random.choice(corgi_photos)
            await self.sender.sendPhoto((choice.split("/")[-1], urlopen(choice)))
        except Exception as e:
            logging.error(e)
            await self.sender.sendPhoto(
                ("cat_photo.jpg",
                 urlopen('http://cdn.meme.am/instances/500x/55452028.jpg')))
