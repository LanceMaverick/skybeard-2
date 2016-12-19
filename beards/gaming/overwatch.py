import re
import logging
import requests
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

def post_news():
    try:
        news = overw_news()[0]
    except IndexError:
        return 'Request failed. Servers may be down'
    if not news:
        return 'No news items found in overwatch  api request'

    header = '*Latest news post* (patch version {})'.format(news['patchVersion'])
    status = 'STATUS: '+news['status']
    reply = '\n'.join([header, status, news['detail']])
    return reply
