#corgibase plugin
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

class CorgiBase(BeardChatHandler):
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
                             user_agent = config.user_agent,
                            )
        subreddit = reddit.subreddit('corgis')
        hot_posts = subreddit.top(time_filter = 'all', limit=100)
        url_list = [post.url for post in hot_posts]
        
        
        try:
            choice = random.choice(url_list)
            extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if any (ext in choice for ext in extensions):       
                await self.sender.sendPhoto((
                    choice.split("/")[-1], 
                    urlopen(choice)))
            else:
                await self.sender.sendMessage(choice)
        except Exception as e:
            logging.error(e)
            await self.sender.sendPhoto((
                "cat_photo.jpg",
                urlopen('http://cdn.meme.am/instances/500x/55452028.jpg')))
       
