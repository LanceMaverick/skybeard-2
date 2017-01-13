import feedparser
from . import config

def parse_feed_info(url):
    feed = feedparser.parse(url)
    items = []
    for item in feed['items']:
        try:
            items.append(dict(
                title = item['title'],
                url = item['links'][0]['href']
                ))
        except KeyError:
            pass

    return items[:config.item_limit]





