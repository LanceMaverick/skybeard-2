import dataset
import random
import string

from . import config


def get_all_keys():
    with dataset.connect(config.db_name) as db:
        table = db['keys']
        return table.all()


def get_key(chat_id):
    with dataset.connect(config.db_name) as db:
        table = db['keys']
        existing_key = table.find_one(chat_id=chat_id)
        if existing_key:
            return existing_key
        else:
            table.insert(
                dict(
                    chat_id=chat_id,
                    key="".join(
                        (random.choice(string.ascii_letters) for x in range(20))
                    )
                )
            )
            return table.find_one(chat_id=chat_id)
