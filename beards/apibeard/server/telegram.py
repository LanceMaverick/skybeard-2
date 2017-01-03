import aiohttp
from skybeard.beards import BeardChatHandler


def make_bot_function(session, meth, key):
    """Makes a function for communicating with the telegram bot."""
    async def g(tg_method, data=None):
        """A thin wrapper around aiohttp method for {}""".format(meth)
        url = "https://api.telegram.org/bot{}/{}".format(key, tg_method)
        resp = await getattr(session, meth)(
                url,
                data=data if data else None
        )
        return resp

    return g


def not_implemented(*args, **kwargs):
    raise NotImplementedError(
        "This function has not yet been created with setup_telegram()")


post = not_implemented
get = not_implemented


def setup_telegram(*args):
    """Sets up telegram functions for the app to use.

    NOTE: this is not a referentially transparent funtion; it relies on the
    BeardChatHandler.key and should not be called until BeardChatHandler has
    been set up.

    """
    global _session
    global post
    global get
    _session = aiohttp.ClientSession()
    post = make_bot_function(_session, 'post', BeardChatHandler.key)
    get = make_bot_function(_session, 'get', BeardChatHandler.key)
