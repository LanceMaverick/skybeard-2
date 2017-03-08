from functools import wraps, partial
from aiohttp import web
import types

class BeardWebApplication(web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_route(self, endpoint_or_fn, endpoint=None, methods=None):
        if isinstance(endpoint_or_fn, str):
            return partial(self.add_route, endpoint=endpoint_or_fn)
        assert isinstance(endpoint_or_fn, types.FunctionType),\
            "This function requires a function or string!"

        ret_func = wraps(endpoint_or_fn)(endpoint_or_fn)

        if methods is None:
            methods = ['POST', 'GET']

        for method in methods:
            add_fn = getattr(app.router, "add_{}".format(method.lower()))
            add_fn(endpoint, ret_func)

        return ret_func



# def async_get(endpoint_or_fn, endpoint=None):
#     if isinstance(endpoint_or_fn, str):
#         return partial(async_get, endpoint=endpoint_or_fn)

#     ret_func = wraps(endpoint_or_fn)(endpoint_or_fn)

#     app.router.add_get(endpoint, ret_func)

#     return ret_func

# def async_post(endpoint_or_fn, endpoint=None):
#     if isinstance(endpoint_or_fn, str):
#         return partial(async_post, endpoint=endpoint_or_fn)

#     ret_func = wraps(endpoint_or_fn)(endpoint_or_fn)

#     app.router.add_post(endpoint, ret_func)

#     return ret_func


app = BeardWebApplication()


@app.add_route('/', methods=['POST'])
async def hello(request):
    return web.json_response({"text": "Hello, world"})

