from skybeard.beards import BeardChatHandler
from skybeard.predicates import Filters


class Echo(BeardChatHandler):

    __userhelp__ = """A simple echo beard. Echos whatever it is sent."""

    # Commands takes tuples like arguments:
    # 1. Condition: Predicate function/string telegram command e.g. "dog"
    #    becomes # /dog
    # 2. Callback: Coroutine or name of member coroutine as a string to call
    #    when condition is met
    # 3. Help: Help text
    __commands__ = [
        # condition,   callback coro,             help text
        (Filters.text,     'echo',      'Echos everything said by anyone.')
    ]

    # __init__ is implicit

    async def echo(self, msg):
        await self.sender.sendMessage(msg['text'])
