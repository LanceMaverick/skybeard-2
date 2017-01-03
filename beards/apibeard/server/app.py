from sanic import Sanic
from sanic.response import json

from . import telegram as tg

app = Sanic(__name__)


@app.route('/')
async def hello_world(x):
    return json(x)


@app.route('/sendMessage', methods=["POST"])
async def send_message(request):
    resp = await tg.post('sendMessage', data=request.json)
    async with resp:
        ret_json = await resp.json()

    return json(ret_json)
