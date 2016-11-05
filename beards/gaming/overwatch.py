import re
import requests
import telegram
from . import config
"""get latest steam news post using given payload parameters"""
def overw_news():
    url = 'https://api.lootbox.eu/patch_notes'
    response = requests.get(url)
    news = response.json()['patchNotes']
    return news

def post_news(bot, update):
    message = update.message
    try:
        news = overw_news()[0]
    except IndexError:
        message.reply_text('Request failed. Servers may be down')
        return 
    if not news:
        message.reply_text('No news items found in overwatch  api request')
        return
    
    header = '*Latest news post* (patch version {})'.format(news['patchVersion'])
    status = 'STATUS: '+news['status']
    reply = '\n'.join([header, status, news['detail']])
    try:
        message.reply_text(reply, parse_mode= 'HTML')
    except telegram.error.BadRequest:
        #remove html if it can't parse it
        message.reply_text(re.sub('<[^<]+?>', '', reply))

