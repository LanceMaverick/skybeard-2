from skybeard.beards import BeardChatHandler
from skybeard.predicates import Filters
from skybeard.utils import get_beard_config


config = get_beard_config()


class Echo(BeardChatHandler):

    __userhelp__ = """A simple echo beard. Echos whatever it is sent."""

    __commands__ = [
        (Filters.text, 'msg_config',
         'Messages the hello_world variable from config.')
    ]

    # __init__ is implicit

    async def msg_config(self, msg):
        # await self.sender.sendMessage(msg['text'])
        await self.sender.sendMessage(config['hello_world'])
