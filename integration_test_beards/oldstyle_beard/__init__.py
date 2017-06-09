from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror


class OldstyleBeard(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        # command, callback coro, help text
        ("test_oldstyle_beard", 'test', 'Tests this beard.')
    ]

    # __init__ is implicit

    @onerror()
    async def test(self, msg):
        await self.sender.sendMessage(
            "Test successful! {self} has been successfully imported and instantiated.".format(
                **locals()))
