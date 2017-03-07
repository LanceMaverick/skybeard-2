from skybeard.beards import BeardChatHandler
from skybeard.bearddbtable import BeardDBTable
from skybeard.decorators import onerror
from skybeard.utils import get_args
from skybeard.server import app, web


class RelayBeard(BeardChatHandler):

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
            await self.sender.sendMessage("Args: {}".format(args))
        else:
            await self.sender.sendMessage("No arguments given.")


RelayBeard.key_table = BeardDBTable(RelayBeard, "key_table")


@app.add_route('/relay{key:[a-zA-Z]+}/{command}', methods=['GET', 'POST'])
async def relay_to_telegram(request):
    command_for_telegram = request.match_info['command']
    key = request.match_info['key']
    return web.json_response({
        "command": command_for_telegram,
        "key": key
    })
