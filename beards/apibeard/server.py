import aiohttp
from sanic import Sanic
from sanic.response import json

from skybeard.beards import BeardChatHandler


app = Sanic(__name__)

# Consider making a class that contains:
# a process running the server
# An aiohttp session
# All the post and get functions
#
# There should also be a `create_sanic_server` function which instantiates the
# class. Or maybe the constructor of the class will be enough.

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


def _after_start(*args):
    global session
    global post
    global get
    session = aiohttp.ClientSession()
    post = make_bot_function(session, 'post', BeardChatHandler.key)
    get = make_bot_function(session, 'get', BeardChatHandler.key)


def start_app(*args, **kwargs):
    app.run(debug=True, after_start=[_after_start])


@app.route('/')
async def hello_world(x):
    return json(x)


@app.route('/sendMessage', methods=["POST"])
async def send_message(request):
    resp = await post('sendMessage', data=request.json)
    async with resp:
        ret_json = await resp.json()

    return json(ret_json)
