from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror, debugonly


class DebugOnlyExample(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        ("debugonlytest", 'debug_only_test',
         'Tests if skybeard is in debug mode.')
    ]

    # __init__ is implicit

    @onerror()
    @debugonly("Skybeard is not in debug mode.")
    async def debug_only_test(self, msg):
        # This message will only be sent if skybeard is run in debug mode
        await self.sender.sendMessage("You are in debug mode!")
