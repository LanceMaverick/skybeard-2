from pathlib import Path

import stringcase


def make_init_text(name):
    init_text = '''
from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror
from skybeard.utils import get_args


class {beardclassname}(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        # command, callback coro, help text
        ("echo", 'echo', 'Echos arguments. e.g. <code>/echo [arg1 [arg2 ... ]]</code>')
    ]

    # __init__ is implicit

    @onerror
    async def echo(self, msg):
        args = get_args(msg)
        if args:
            await self.sender.sendMessage("Args: {{}}".format(args))
        else:
            await self.sender.sendMessage("No arguments given.")

    '''.strip().format(beardclassname=stringcase.pascalcase(name))

    return init_text
