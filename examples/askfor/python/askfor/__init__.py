from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror, askfor
from skybeard.utils import get_args


class Askfor(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        # command, callback coro, help text
        ("askforstuff", 'ask_for_stuff', 'Asks for two arguments and echos them back.')
    ]

    # __init__ is implicit

    @onerror
    @askfor([('var_x', "What's your first variable?"),
             ('var_y', "What's your second variable?")])
    async def ask_for_stuff(self, msg, var_x, var_y):
        await self.sender.sendMessage("1) {}\n2) {}".format(
            var_x, var_y))
