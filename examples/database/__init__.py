import logging
import random
from skybeard.beards import BeardChatHandler, BeardDBTable
from skybeard.decorators import onerror

logger = logging.getLogger(__name__)


class Database(BeardChatHandler):

    __userhelp__ = "A demonstration beard for <code>BeardDBTable</code>."

    __commands__ = [
        ("write", 'write_to_db', 'Writes a random value to database'),
        ("lastwritten", 'last_written_to_db',
         'Reads the last value written to the database.'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("Creating BeardDBTable.")
        self.test_table = BeardDBTable(self, 'test')

    @onerror
    async def write_to_db(self, msg):
        random_number = random.random()
        await self.sender.sendMessage(
            "Attempting to write value to db: {}".format(random_number))
        with self.test_table as table:
            table.insert(dict(random_number=random_number))

    @onerror
    async def last_written_to_db(self, msg):
        with self.test_table as table:
            for x in table.all():
                last_value = x

        await self.sender.sendMessage(
            "Last entry: {}".format(last_value['random_number']))
