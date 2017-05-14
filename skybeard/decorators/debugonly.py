from functools import wraps, partial
import logging

logger = logging.getLogger(__name__)


def debugonly(text="This command can only be run in debug mode.", **kwargs):
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

    def wrapper(f):
        @wraps(f)
        async def g(beard, *fargs, **fkwargs):
            if logger.getEffectiveLevel() <= logging.DEBUG:
                return await f(beard, *fargs, **fkwargs)
            else:
                await beard.sender.sendMessage(
                    text,
                    **kwargs,
                )
                return
        return g
    return wrapper
