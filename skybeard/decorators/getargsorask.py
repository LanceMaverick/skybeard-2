from collections import OrderedDict
from functools import wraps, partial

from ..utils import get_args


def getargsorask(vars_n_qs):
    """A combination of getargs and askfor decorator.

    If the args are not provided during the function call, they will be asked
    for the same way askfor asks for things.

    """
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
