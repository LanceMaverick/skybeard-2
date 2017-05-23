from collections import OrderedDict
from functools import wraps


def askfor(vars_n_qs):
    """Ask for variables given to a function.

    .. code:: python
        @askfor([('var_x', "What's your first variable?"),
                ('var_y', "What's your second variable?")])
        async def ask_for_stuff(self, msg, var_x, var_y):
            await self.sender.sendMessage("1) {}\n2) {}".format(
                var_x, var_y))

    Will result in:
    > /askforstuff
    < What's your first variable?
    > 123
    < What's your second variable?
    > 456
    < 1) 123
      2) 456

    """

    def wrapper(f):
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
    return wrapper
