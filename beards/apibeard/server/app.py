import logging

import sanic
from sanic import Sanic, Blueprint
from sanic.response import json, text
from sanic.exceptions import NotFound

try:
    from sanic_cors import CORS
except ImportError:
    assert False, "Missing dependency (sanic_cors). To install: pip install https://github.com/ashleysommer/sanic-cors/"

from skybeard.beards import Beard

from . import telegram as tg
from .. import database
# from . import utils

logger = logging.getLogger(__name__)


app = Sanic(__name__)

# CORS: https://en.wikipedia.org/wiki/Cross-origin_resource_sharing
CORS(app)
key_blueprint = Blueprint('key', url_prefix='/key[A-z]+')


@app.route('/')
async def hello_world(request):
    return text(
        ("Hello World! Your API beard is working! "
         "Running Sanic version: {}. Beards running: {}.").format(
             sanic.__version__,
             Beard.beards
    ))


@app.route('/loadedBeards', methods=["GET"])
async def loaded_beards(request):
    return json([str(x) for x in Beard.beards])


@key_blueprint.route('/relay/<method:[A-z]+>', methods=["POST", "GET"])
async def relay_tg_request(request, method):
    """Acts as a proxy for telegram's sendMessage."""
    resp = await getattr(tg, request.method.lower())(
        'sendMessage', data=request.json)
    async with resp:
        ret_json = await resp.json()

    return json(ret_json)


# blueprint middleware is global! Only use app for clarity.
@app.middleware('request')
async def authentication(request):
    if "key" not in request.url:
        return
    if not database.is_key_match(request.url):
        raise NotFound(
            "URL not found or key not recognised.")

app.blueprint(key_blueprint)
