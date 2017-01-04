from sanic import Sanic
from sanic.response import json

from . import telegram as tg


app = Sanic(__name__)


@app.route('/')
async def hello_world(request):
    return "Hello World! Your API beard is working!"


@app.route('/relay/<method:[A-z]+>', methods=["POST", "GET"])
async def relay_tg_request(request, method):
    """Acts as a proxy for telegram's sendMessage."""
    resp = await getattr(tg, request.method.lower())(
        'sendMessage', data=request.json)
    async with resp:
        ret_json = await resp.json()

    return json(ret_json)
