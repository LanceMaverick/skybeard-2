import re
import logging
import requests
import telegram
from . import config
from json.decoder import JSONDecodeError

"""get latest steam news post using given payload parameters"""
def overw_news():
    url = 'https://api.lootbox.eu/patch_notes'
    response = requests.get(url)
    try:
        news = response.json()['patchNotes']
    except JSONDecodeError as e:
        logging.error(e, response.text)
        return []
    return news

def post_news(bot, update):
    message = update.message
    try:
        news = overw_news()[0]
    except IndexError:
        message.reply_text('Request failed. Servers may be down', quote= False)
        return 
    if not news:
        message.reply_text('No news items found in overwatch  api request', quote= False)
        return
    
    header = '*Latest news post* (patch version {})'.format(news['patchVersion'])
    status = 'STATUS: '+news['status']
    reply = '\n'.join([header, status, news['detail']])
    try:
        message.reply_text(reply, parse_mode= 'HTML', quote= False)
    except telegram.error.BadRequest:
        #remove html if it can't parse it
        message.reply_text(re.sub('<[^<]+?>', '', reply), quote= False)

