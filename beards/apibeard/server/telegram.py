import aiohttp
from skybeard.beards import BeardChatHandler


def make_bot_function(session, meth, key):
    async def g(tg_method, data=None):
        """A thin wrapper around aiohttp method for {}""".format(meth)
        url = "https://api.telegram.org/bot{}/{}".format(key, tg_method)
        resp = await getattr(session, meth)(
                url,
                data=data if data else None
        )
        return resp

    return g


def setup_telegram(*args):
    global session
    global post
    global get
    session = aiohttp.ClientSession()
    post = make_bot_function(session, 'post', BeardChatHandler.key)
    get = make_bot_function(session, 'get', BeardChatHandler.key)
