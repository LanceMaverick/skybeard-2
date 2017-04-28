from collections import OrderedDict
from functools import wraps, partial


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
