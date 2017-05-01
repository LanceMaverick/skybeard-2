from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror, askfor, getargsorask, getargs


class Askfor(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        # command, callback coro, help text
        ("getargs", 'get_args', 'Gets two arguments and sends then back.'),
        ("askforstuff", 'ask_for_stuff', 'Asks for two arguments and echos them back.'),
        ("optionalargsdemo", 'optional_args_demo', 'Asks for arguments if not provided (2 args.)'),
    ]

    # __init__ is implicit

    @onerror()
    @getargs()
    async def get_args(self, msg, var_x, var_y):
        await self.sender.sendMessage("1) {}\n2) {}".format(
            var_x, var_y))

    @onerror()
    @askfor([('var_x', "What's your first variable?"),
             ('var_y', "What's your second variable?")])
    async def ask_for_stuff(self, msg, var_x, var_y):
        await self.sender.sendMessage("1) {}\n2) {}".format(
            var_x, var_y))

    @onerror()
    @getargsorask([('var_x', "What's your first variable?"),
                   ('var_y', "What's your second variable?")])
    async def optional_args_demo(self, msg, var_x, var_y):
        await self.sender.sendMessage("1) {}\n2) {}".format(
            var_x, var_y))
