from functools import wraps
import pyconfig


def admin():
    """A decorator for checking if the sender of a message
    is in the admins list of config.py. Will not call the
    coro if not"""
    # if isinstance(f_or_text, str):
    #     return partial(admin, text=f_or_text, **kwargs)
    # elif f_or_text is None:
    #     return partial(admin, **kwargs)

    def wrapper(f):
        @wraps(f)
        # async def g(beard, *fargs, **fkwargs):
        async def g(beard, msg, *fargs, **fkwargs):
            if msg['from']['id'] in pyconfig.get('admins'):
                return await f(beard, msg, *fargs, **fkwargs)
            else:
                return await beard.sender.sendMessage(
                    "This command can only be run by an admin")
        return g
    return wrapper
