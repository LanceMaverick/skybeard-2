from functools import wraps


def onerror(f):
    @wraps(f)
    async def g(beard, *fargs, **fkwargs):
        try:
            return await f(beard, *fargs, **fkwargs)
        except Exception as e:
            await beard.__onerror__(e)
            raise e

    return g
