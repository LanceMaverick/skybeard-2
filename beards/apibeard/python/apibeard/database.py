import dataset
import random
import string
import functools
import logging
import re

from . import config

logger = logging.getLogger(__name__)


def get_all_keys():
    with dataset.connect(config.db_name) as db:
        table = db['keys']
        return table.all()


def make_key(chat_id):
    """Make key."""
    with dataset.connect(config.db_name) as db:
        table = db['keys']
        return table.insert(
            dict(
                chat_id=chat_id,
                key="".join(
                    (random.choice(string.ascii_letters) for x in range(20))
                )
            )
        )


@functools.lru_cache()
def get_key(chat_id):
    """Get key.

    If key exists, get key. If key does not exist, create key and get it.

    """
    with dataset.connect(config.db_name) as db:
        table = db['keys']
        existing_key = table.find_one(chat_id=chat_id)
        if existing_key:
            return existing_key
        else:
            make_key(chat_id)

    return get_key(chat_id)


@functools.lru_cache()
def is_key_match(url):

    matches = re.findall(r"/key([A-z]+)/.*", url)
    logger.debug("Matches found: {}".format(matches))
    if not matches:
        return

    key = matches[0]
    logger.debug("Key is: {}".format(key))
    with dataset.connect(config.db_name) as db:
        table = db['keys']
        if table.find_one(key=key):
            return True
