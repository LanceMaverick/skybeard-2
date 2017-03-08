import string
import random

import pyconfig

from skybeard.beards import BeardChatHandler
from skybeard.bearddbtable import BeardDBTable
from skybeard.decorators import onerror, admin
from skybeard.server import app, web


async def make_key():
    """Makes key for relay commands."""
    return "".join([random.choice(string.ascii_letters) for x in range(20)])


class RelayBeard(BeardChatHandler):

    __userhelp__ = """This beard sets up a relay point for telegram commands.

To use, get a key with /getrelaykey and then you can relay commands to the bot using the following syntax:

<code>&lt;hostname&gt;:&lt;port&gt;/relay&lt;key&gt;/&lt;telegram api endpoint&gt;</code>
    """

    __commands__ = [
        ('getrelaykey', 'get_key', 'Gets key for relay commands.'),
        ('revokerelaykey', 'revoke_key', 'Revokes your personal relay key.')
    ]

    # __init__ is implicit

    @admin
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

    @admin
    @onerror
    async def revoke_key(self, msg):
        with type(self).key_table as table:
            e = table.find_one(user_id=msg['from']['id'])
            if e:
                table.delete(**e)
                await self.sender.sendMessage("Key revoked.")
            else:
                await self.sender.sendMessage("No key to revoke.")


RelayBeard.key_table = BeardDBTable(RelayBeard, "key_table")


@app.add_route('/relay{key:[a-zA-Z]+}/{command}', methods=['GET', 'POST'])
async def relay_to_telegram(request):
    command_for_telegram = request.match_info['command']
    key = request.match_info['key']
    with RelayBeard.key_table as table:
            e = table.find_one(key=key)

    session = pyconfig.get('aiohttp_session')
    if e:
        if await request.read():
            data = await request.json()
        else:
            data = None
        async with session.request(
                request.method,
                "https://api.telegram.org/bot{botkey}/{cmd}".format(
                    botkey=pyconfig.get('key'),
                    cmd=command_for_telegram),
                data=data) as resp:
            ret_json = await resp.json()

    return web.json_response(ret_json)
