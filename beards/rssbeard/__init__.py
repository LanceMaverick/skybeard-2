import logging
import re
import telepot
import telepot.aio
from telepot import glance, message_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.utils import get_args
from . import rss
from . import config

class RssBeard(BeardChatHandler):

    __commands__ = [
            ('listfeeds', 'list_feeds', 'show which feeds are available'),
            ('feed', 'send_feed', 'Takes argument of which feed to see (as given by /listfeeds)')
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

    async def send_feed(self, msg):
        try:
            query_id, from_id, query_data = glance(
                    msg, 
                    flavor='callback_query')
        except Exception as e:
            #don't know what it is yet...
            print(e)
            try:
                arg = get_args(msg)[0]
            except:
                await self.send_feed_keyboard(msg)
                return
        else:
            try:
                arg = self.deserialize(query_data)
            except ThatsNotMineException:
                return
        try:
            feed_url = config.feeds[arg][0]
            feed_name = config.feeds[arg][1]
        except KeyError:
            await self.sender.sendMessage('I do not recognise that feed')
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

    async def send_feed_keyboard(self, msg):
        keyboard = InlineKeyboardMarkup(
                inline_keyboard = [[InlineKeyboardButton(
                    text = v[1],
                    callback_data = self.serialize(k))]
                    for k, v in config.feeds.items()])
        await self.sender.sendMessage(
                text = 'List of feeds:',
                reply_markup = keyboard)

    async def on_callback_query(self, msg):
        await self.send_feed(msg)






