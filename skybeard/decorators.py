from functools import wraps, partial
import logging

logger = logging.getLogger(__name__)


def onerror(f_or_text=None, **kwargs):
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
    if isinstance(f_or_text, str):
        return partial(onerror, text=f_or_text, **kwargs)
    elif f_or_text is None:
        return partial(onerror, **kwargs)

    @wraps(f_or_text)
    async def g(beard, *fargs, **fkwargs):
        try:
            return await f_or_text(beard, *fargs, **fkwargs)
        except Exception as e:
            if kwargs:
                await beard.sender.sendMessage(**kwargs)
            else:
                await beard.sender.sendMessage(
                    "Sorry, something went wrong")

            await beard.__onerror__(e)
            raise e

    return g


def debugonly(f):
    @wraps(f)
    async def g(beard, *fargs, **fkwargs):
        if logger.getEffectiveLevel() <= logging.DEBUG:
            return await f(beard, *fargs, **fkwargs)
        else:
            return await beard.sender.sendMessage(
                "This command can only be run in debug mode.")

    return g
