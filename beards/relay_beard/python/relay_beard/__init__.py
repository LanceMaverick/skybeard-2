import string
import random

from skybeard.beards import BeardChatHandler
from skybeard.bearddbtable import BeardDBTable
from skybeard.decorators import onerror
from skybeard.server import app, web
from skybeard.predicates import regex_predicate


async def make_key():
    """Makes key for relay commands."""
    return "".join([random.choice(string.ascii_letters) for x in range(20)])


class RelayBeard(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        # command, callback coro, help text
        (regex_predicate("_getkey"), 'get_key', 'Gets key for relay commands')
    ]

    # __init__ is implicit

    @onerror
    async def get_key(self, msg):
        with type(self).key_table as table:
            e = table.find_one(user_id=msg['from']['id'])
            if not e:
                table.insert(
                    dict(
                        user_id=msg['from']['id'],
                        key=await make_key()
                    ))
                e = table.find_one(user_id=msg['from']['id'])

        await self.sender.sendMessage("Key is: {}".format(e['key']))


RelayBeard.key_table = BeardDBTable(RelayBeard, "key_table")


@app.add_route('/relay{key:[a-zA-Z]+}/{command}', methods=['GET', 'POST'])
async def relay_to_telegram(request):
    command_for_telegram = request.match_info['command']
    key = request.match_info['key']
    return web.json_response({
        "command": command_for_telegram,
        "key": key
    })
