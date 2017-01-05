from functools import wraps
import logging

logger = logging.getLogger(__name__)


def onerror(f):
    @wraps(f)
    async def g(beard, *fargs, **fkwargs):
        try:
            return await f(beard, *fargs, **fkwargs)
        except Exception as e:
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
