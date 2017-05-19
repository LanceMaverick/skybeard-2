from functools import wraps
import re

from ..utils import get_args


def getargs(return_string=None):
    """Gets the arguments from a given command.

    Expects a function with the arguments like so:
        @getargs()
        async def f(self, msg, arg1, arg2):
            # Do things

    If arguments are not provided, gives standard error messages.

    """
    def wrapper(f):
        @wraps(f)
        async def g(beard, msg):
            args = get_args(msg, return_string=return_string)
            try:
                if isinstance(args, str):
                    await f(beard, msg, args)
                else:
                    await f(beard, msg, *args)
            except TypeError as exception:
                # TODO have configurable messages when args are not enough
                err_msg = exception.args[0]
                if err_msg.startswith(f.__name__+"() missing"):
                    text = err_msg.replace("get_args() ", "")
                    text = text[0].upper() + text[1:]
                elif err_msg.startswith(f.__name__+"() takes"):
                    args_expected, args_given = re.findall(r"\d", err_msg)
                    args_given = int(args_given) - 2
                    args_expected = int(args_expected) - 2
                    text = "Too many arguments given. (got {}, expected {})".format(
                        args_given, args_expected)
                else:
                    # Else, it's not a problem with the function arguments
                    raise exception

                beard.logger.debug("Exception message was: {}".format(err_msg))
                await beard.sender.sendMessage(text)
                return

        return g

    return wrapper
