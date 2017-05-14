from functools import wraps


def onerror(text=None, **kwargs):
    """A decorator for sending a message to the user on an exception.

    If no arguments are used (i.e. the function is passed directly to the
    decorator), beard.__onerror__(exception) is called if the decorated
    function excepts.

    If a string is passed as the first argument, then the decorated function
    sends this message instead of calling the beard.__onerror__ function.
    kwargs are passed to beard.sender.sendMessage and
    beard.__onerror__(exception) is called.

    If only kwargs are passed, then the decorated function attempts
    beard.sender.sendMessage(**kwargs) and then calls
    beard.__onerror__(exception).
    """

    def wrapper(f):
        @wraps(f)
        async def g(beard, *fargs, **fkwargs):
            try:
                return await f(beard, *fargs, **fkwargs)
            except Exception as e:
                if text or kwargs:
                    await beard.sender.sendMessage(text, **kwargs)
                else:
                    await beard.sender.sendMessage(
                        "Sorry, something went wrong")

                await beard.__onerror__(e)
                raise e

        return g
    return wrapper
