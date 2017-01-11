import logging

from sanic import Sanic, Blueprint
from sanic.response import json
from sanic.exceptions import NotFound

from . import telegram as tg
from . import utils

logger = logging.getLogger(__name__)


app = Sanic(__name__)
key_blueprint = Blueprint('key', url_prefix='/key[A-z]+')


@app.route('/')
async def hello_world(request):
    return "Hello World! Your API beard is working!"


@key_blueprint.route('/relay/<method:[A-z]+>', methods=["POST", "GET"])
async def relay_tg_request(request, method):
    """Acts as a proxy for telegram's sendMessage."""
    resp = await getattr(tg, request.method.lower())(
        'sendMessage', data=request.json)
    async with resp:
        ret_json = await resp.json()

    return json(ret_json)


@key_blueprint.middleware('request')
async def authentication(request):
    if not utils.is_key_match(request.url):
        raise NotFound(
            "URL not found or key not recognised.")

app.register_blueprint(key_blueprint)
