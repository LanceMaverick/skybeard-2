"""This module is responsible for running the server.

It is made in a functional programming style. For more information see
https://en.wikipedia.org/wiki/Functional_programming.

"""

from multiprocessing import Process


from .app import app
from .telegram import setup_telegram


def _start_server(the_app, *args, **kwargs):
    return the_app.run(*args, **kwargs)


def start(debug=False):
    """Starts the Sanic server.

    This functions starts the Sanic server and sets up the telegram functions
    for the app to use.

    Returns the started process.

    """
    global proc
    proc = Process(
        target=_start_server,
        args=(
            app,
        ),
        kwargs=dict(
            debug=debug,
            after_start=[setup_telegram]
        )
    )
    proc.start()
    return proc


def stop():
    global proc
    return proc.stop()
