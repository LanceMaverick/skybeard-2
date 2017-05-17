from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror, admin

import pyconfig


class ConfigHelper(BeardChatHandler):

    __userhelp__ = """Simple config helper beard."""

    __commands__ = [
        # command, callback coro, help text
        ("getconfig", 'getconfig', 'Gets the config for skybeard (admin only).')
    ]

    # __init__ is implicit

    @onerror()
    @admin()
    async def getconfig(self, msg):
        await self.sender.sendDocument(open(pyconfig.get('config_file')))
