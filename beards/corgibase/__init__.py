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

logger = logging.getLogger(__name__)

class CorgiBase(BeardChatHandler):
    __userhelp__ = """
    Say give me corgis or show me corgis to see some corgis!"""
    __commands__ = [
            (
                regex_predicate('(give|show) me corgis', lower = True), 
                'send_corgi', 
                'send a random corgi image from reddit'),
            (
                regex_predicate('(give|show) me sausage dogs', lower = True), 
                'send_sausage', 
                'send a random dachshund image from reddit'),]

    async def send_corgi(self, msg):
        await self.send_reddit_rand(msg, 'corgis')

    async def send_sausage(self, msg):
        await self.send_reddit_rand(msg, 'dachshund')


    async def send_reddit_rand(self, msg, sub):
        reddit = praw.Reddit(client_id = config.client_id, 
                             client_secret = config.client_secret,
                             username = config.username,
                             password = config.password,
                             user_agent = config.user_agent,
                            )
        subreddit = reddit.subreddit(sub)
        hot_posts = subreddit.top(time_filter = 'all', limit=100)
        url_list = [post.url for post in hot_posts]
        
        
        try:
            choice = random.choice(url_list)
            extensions = ['.jpg', '.jpeg', '.png']
            if any (ext in choice for ext in extensions):       
                await self.sender.sendPhoto((
                    choice.split("/")[-1], 
                    urlopen(choice)))
            else:
                await self.sender.sendMessage(choice)
        except Exception as e:
            logger.error(e, choice)
            await self.sender.sendPhoto((
                "cat_photo.jpg",
                urlopen('http://cdn.meme.am/instances/500x/55452028.jpg')))
       
