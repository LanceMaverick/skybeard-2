"""This module is responsible for running the server.

It is made in a functional programming style. For more information see
https://en.wikipedia.org/wiki/Functional_programming.

"""

from multiprocessing import Process

# for https://github.com/channelcat/sanic/issues/275
import asyncio
import sanic
from sanic.server import HttpProtocol

from .app import app
from .telegram import setup_telegram


def _start_server(the_app, *args, **kwargs):
    return the_app.run(*args, **kwargs)


# from https://github.com/channelcat/sanic/issues/275
async def run_web_app(app, port, *, loop, logger, request_timeout=20):
    connections = {}
    signal = sanic.server.Signal()
    handler_factory = lambda: HttpProtocol(
        loop = loop,
        connections = connections,
        signal = signal,
        request_handler = app.handle_request,
        request_timeout = request_timeout,
        request_max_size = 1024*1024
    )

    server = await loop.create_server(handler_factory, None, port)
    for sock in server.sockets:
        sockname = sock.getsockname()
        logger.info("Listening on %s:%d", sockname[0], sockname[1])

    try:
        await asyncio.Future(loop=loop)
    finally:
        server.close()
        await server.wait_closed()

        # Complete all tasks on the loop
        signal.stopped = True
        for connection in connections.keys():
            connection.close_if_idle()
        while connections:
            await asyncio.sleep(0.1, loop=loop)


def start(debug=False):
    """Starts the Sanic server.

    This functions starts the Sanic server and sets up the telegram functions
    for the app to use.

    Returns the started process.

    """
    # global proc
    # proc = Process(
    #     target=_start_server,
    #     args=(
    #         app,
    #     ),
    #     kwargs=dict(
    #         debug=debug,
    #         after_start=setup_telegram
    #     )
    # )
    # proc.start()
    # return proc
    import logging
    logger = logging.getLogger("async_sanic")
    
    coro = run_web_app(app, 8000, loop=asyncio.get_event_loop(), logger=logger)
    return asyncio.ensure_future(coro)


def stop():
    global proc
    return proc.stop()
