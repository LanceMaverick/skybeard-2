from collections import OrderedDict
from functools import wraps

from ..utils import get_args


def getargsorask(vars_n_qs, return_string=False):
    """A combination of getargs and askfor decorator.

    If the args are not provided during the function call, they will be asked
    for the same way askfor asks for things.

    """
    def _getargsorask_wrapper(f):
        @wraps(f)
        async def g(beard, msg):
            args = get_args(msg, return_string)

            # If return_string is enabled, the 'args' will be a single string.
            # Convert this into a single item argument list.
            if return_string:
                args = [args]

            kwargs = dict()
            for (i, (var, question)) in enumerate(OrderedDict(vars_n_qs).items()):
                try:
                    kwargs[var] = args[i]
                except IndexError:
                    await beard.sender.sendMessage(question)
                    # TODO something fancy if there's a timeout here
                    resp = await beard.listener.wait()
                    kwargs[var] = resp['text']

            return await f(beard, msg, **kwargs)
        return g
    return _getargsorask_wrapper
