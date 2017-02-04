#show spacecats test plugin
# Adapted from work by LanceMaverick
import random
import logging
from urllib.request import urlopen
import telepot
import telepot.aio
import praw
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from . import config

class corgibase(BeardChatHandler):
    __userhelp__ = """
    Say give me corgis or show me corgis to see some corgis!"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command(
        regex_predicate('(give|show) me corgis'), self.send_corgi)

    async def send_corgi(self, msg):
        reddit = praw.Reddit(client_id = config.client_id, 
                             client_secret = config.client_secret,
                             username = config.username,
                             password = config.password,
                            )
        subreddit = reddit.subreddit('corgis')
        hot_posts = subreddit.hot(limit=10)
        url_list = [post.url for post in hot_posts]


#        corgi_photos= [
 #               'http://i.imgur.com/vE7TLA2.jpg',
#		'https://i.imgur.com/v0ZzD8O.jpg',
#		'http://i.imgur.com/XBNueYD.jpg',
#		'http://i.imgur.com/ATa8cDd.jpg',
 #               ]

        try:
            choice = random.choice(url_list)
            await self.sender.sendPhoto((choice.split("/")[-1], urlopen(choice)))
        except Exception as e:
            logging.error(e)
            await self.sender.sendPhoto(
                ("cat_photo.jpg",
                 urlopen('http://cdn.meme.am/instances/500x/55452028.jpg')))
