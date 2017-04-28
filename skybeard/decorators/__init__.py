from collections import OrderedDict
from functools import wraps, partial
import logging
import pyconfig

from ..utils import get_args

logger = logging.getLogger(__name__)


# TODO move this stuff to a file per decorator


def getargs(text, return_string=None):
    """Gets the arguments from a given command.

    Expects a function with the arguments like so:
        async def f(self, msg, args):
            # Do things

    """
    return partial(_getargs,
                   text=text,
                   return_string=return_string)


def _getargs(f, text="No args provided.", return_string=None):
    """See getargs for docs."""
    @wraps(f)
    async def g(beard, msg):
        args = get_args(msg, return_string=return_string)
        if not args:
            await beard.sender.sendMessage(text)
            return

        await f(beard, msg, args)

    return g


def getargsorask(vars_n_qs):
    """TODO docs."""
    return partial(_getargsorask,
                   vars_n_qs=vars_n_qs)


def _getargsorask(f, vars_n_qs):
    @wraps(f)
    async def g(beard, msg):
        args = get_args(msg)
        kwargs = dict()
        for (i, (var, question)) in enumerate(OrderedDict(vars_n_qs).items()):
            try:
                kwargs[var] = args[i]
            except IndexError:
                await beard.sender.sendMessage(question)
                # TODO something fancy if there's a timeout here
                resp = await beard.listener.wait()
                kwargs[var] = resp['text']

        await f(beard, msg, **kwargs)

    return g


def askfor(vars_n_qs):
    """TODO docs."""
    return partial(_askfor,
                   vars_n_qs=vars_n_qs)


def _askfor(f, vars_n_qs):
    @wraps(f)
    async def g(beard, msg):
        kwargs = dict()
        for var, question in OrderedDict(vars_n_qs).items():
            await beard.sender.sendMessage(question)
            # TODO something fancy if there's a timeout here
            resp = await beard.listener.wait()
            kwargs[var] = resp['text']

        await f(beard, msg, **kwargs)

    return g


# def admin(f_or_text=None, **kwargs):
def admin(f):
    """A decorator for checking if the sender of a message
    is in the admins list of config.py. Will not call the
    coro if not"""
    # if isinstance(f_or_text, str):
    #     return partial(admin, text=f_or_text, **kwargs)
    # elif f_or_text is None:
    #     return partial(admin, **kwargs)

    @wraps(f)
    # async def g(beard, *fargs, **fkwargs):
    async def g(beard, msg, *fargs, **fkwargs):
        if msg['from']['id'] in pyconfig.get('admins'):
            return await f(beard, msg, *fargs, **fkwargs)
        else:
            return await beard.sender.sendMessage(
                "This command can only be run by an admin")

    return g


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


def debugonly(f_or_text=None, **kwargs):
    """A decorator to prevent commands being run outside of debug mode.

    If the function is awaited when skybeard is not in debug mode, it sends a
    message to the user. If skybeard is run in debug mode, then it executes the
    body of the function.

    If passed a string as the first argument, it sends that message instead of
    the default message when not in debug mode.

    e.g.

    .. code:: python

      @debugonly("Skybeard is not in debug mode.")
      async def foo(self, msg):
          # This message will only be sent if skybeard is run in debug mode
          await self.sender.sendMessage("You are in debug mode!")

    """

    if isinstance(f_or_text, str):
        return partial(onerror, text=f_or_text, **kwargs)
    elif f_or_text is None:
        return partial(onerror, **kwargs)

    @wraps(f_or_text)
    async def g(beard, *fargs, **fkwargs):
        if logger.getEffectiveLevel() <= logging.DEBUG:
            return await f_or_text(beard, *fargs, **fkwargs)
        else:
            return await beard.sender.sendMessage(
                "This command can only be run in debug mode.")

    return g
