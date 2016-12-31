from functools import wraps


def onerror(f):
    @wraps(f)
    async def g(beard, *fargs, **fkwargs):
        try:
            return await f(beard, *fargs, **fkwargs)
        except Exception as e:
            if hasattr(beard, '__onerror__'):
                await beard.__onerror__(e)
            else:
                await beard.sender.sendMessage(
                    "Sorry, something went wrong with {}".format(beard))
            raise e

    return g
