from functools import wraps, partial

from ..utils import get_args


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
