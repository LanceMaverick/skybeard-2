"""Test 'suite' for apibeard."""

# import aiohttp

from .server import telegram


async def get(url, **kwargs):
    async with telegram._session.get(url, **kwargs) as response:
        return await response


async def main(bot, msg):
    # Get the default reponse
    resp = await get('127.0.0.1:8000')
    bot.sender.sendMessage("Response recieved: {}".format(resp))
