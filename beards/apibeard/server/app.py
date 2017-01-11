import logging

from sanic import Sanic, Blueprint
from sanic.response import json
from sanic.exceptions import NotFound

from . import telegram as tg
# from . import utils

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
    # apibeard must be loaded after everything, since it's a circular
    # dependency.
    #
    # If it is loaded when this file (app.py) is first loaded inside
    # ../apibeard.py, the Python interpreter has not finished loading
    # ../apibeard.py so it only imports part of the file. Importing inside the
    # function avoids this problem, since this function is only called once all
    # files are loaded.
    from .. import apibeard
    if not apibeard.APIBeard.is_key_match(request.url):
        raise NotFound(
            "URL not found or key not recognised.")

app.blueprint(key_blueprint)
