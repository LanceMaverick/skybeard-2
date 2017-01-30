"""Test 'suite' for apibeard."""

# import aiohttp
from yarl import URL
import json

from .server import telegram


async def get_text(url, **kwargs):
    async with telegram._session.get(url, **kwargs) as response:
        return await response.text()


async def get_json(url, **kwargs):
    async with telegram._session.get(url, **kwargs) as response:
        return await response.json()


async def main(bot, msg):
    # Get the default reponse
    resp = await get_text(URL('http://127.0.0.1:8000/'))
    await bot.sender.sendMessage("Response recieved: {}".format(resp))
    await bot.sender.sendMessage("What's your key for the skybeard api?")
    resp = await bot.listener.wait()
    url = URL(
        "http://127.0.0.1:8000/key{}/relay/sendMessage".format(resp['text']))
    data = {'text': 'Test relay successful!', 'chat_id': bot.chat_id}
    resp = await get_json(url, data=json.dumps(data))
    await bot.sender.sendMessage("Response recieved: {}".format(resp))

