from collections import OrderedDict
from functools import wraps, partial


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

