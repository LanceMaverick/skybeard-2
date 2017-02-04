from aiohttp import web
from functools import wraps, partial

app = web.Application()


def async_get(endpoint_or_fn, endpoint=None):
    if isinstance(endpoint_or_fn, str):
        return partial(async_get, endpoint=endpoint_or_fn)

    ret_func = wraps(endpoint_or_fn)(endpoint_or_fn)

    app.router.add_get(endpoint, ret_func)

    return ret_func


@async_get('/')
async def hello(request):
    return web.json_response({"text": "Hello, world"})

# app.router.add_get('/', hello)
