import logging
import re
import telepot
import telepot.aio
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler
from skybeard.utils import get_args
from . import rss
from . import config

class RssBeard(BeardChatHandler):

    __commands__ = [
            ('listfeeds', 'list_feeds', 'show which feeds are available'),
            ('feed', 'get_feed', 'Takes argument of which feed to see (as given by /listfeeds)')
            ]

    __userhelp__ = """
    See headlines from RSS feeds
    """ 
    async def list_feeds(self, msg):

        feed_strings = ['*Available feeds:*']

        for feed in config.feeds.keys():
            feed_strings.append(feed)

        await self.sender.sendMessage(
                '\n'.join(feed_strings), 
                parse_mode = 'markdown')

    async def get_feed(self, msg):
        try:
            arg = get_args(msg)[0]
        except:
            await self.sender.sendMessage('Please specify a feed')
            return

        try:
            feed_url = config.feeds[arg][0]
            feed_name = config.feeds[arg][1]
        except KeyError:
            await self.sendMessage('I do not recognise that feed')
            return

        items = rss.parse_feed_info(feed_url)
        
        await self.sender.sendMessage(
                'Top {} front page items for {}:'.format(
                    config.item_limit, 
                    feed_name),
                reply_markup = self.make_keyboard(items))

    def make_keyboard(self, items):
        keyboard = InlineKeyboardMarkup(
                inline_keyboard = [[InlineKeyboardButton(
                    text = item['title'],
                    url = item['url'])]
                    for item in items])
        return keyboard


