import re
import logging

from sanic import Sanic, Blueprint
from sanic.response import json
from sanic.exceptions import NotFound

from . import telegram as tg

logger = logging.getLogger(__name__)


app = Sanic(__name__)
blueprint = Blueprint('key', url_prefix='/key[A-z]+')


@app.route('/')
async def hello_world(request):
    return "Hello World! Your API beard is working!"


@blueprint.route('/relay/<method:[A-z]+>', methods=["POST", "GET"])
async def relay_tg_request(request, method):
    """Acts as a proxy for telegram's sendMessage."""
    resp = await getattr(tg, request.method.lower())(
        'sendMessage', data=request.json)
    async with resp:
        ret_json = await resp.json()

    return json(ret_json)

allowed_keys = {"abcd"}


def is_key_match(url):
    match = re.match(r"/key([A-z]+)/.*", url)
    key = match.group(1)
    logger.debug("Matches found: {}".format(match))
    logger.debug("Key is: {}".format(key))
    if match:
        if key in allowed_keys:
            return True

    return False


@blueprint.middleware('request')
async def authentication(request):
    if not is_key_match(request.url):
        raise NotFound(
            "URL not found or key not recognised.")

app.register_blueprint(blueprint)
