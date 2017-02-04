#!/usr/bin/env python
import os
import asyncio
import logging
import itertools
import importlib
import argparse
import pyconfig

import telepot
from telepot.aio.delegate import (per_chat_id,
                                  create_open,
                                  pave_event_space,
                                  include_callback_query_chat_id)

from skybeard.beards import Beard, BeardChatHandler, SlashCommand
from skybeard.help import create_help
from skybeard.utils import (is_module,
                            contains_setup_beard_py,
                            get_literal_path,
                            get_literal_beard_paths,
                            all_possible_beards,
                            PythonPathContext)
import config

logger = logging.getLogger(__name__)


class DuplicateCommand(Exception):
    pass


# def is_module(filename):
#     fname, ext = os.path.splitext(filename)
#     if ext == ".py":
#         return True
#     elif os.path.exists(os.path.join(filename, "__init__.py")):
#         return True
#     else:
#         return False


# def get_literal_path(path_or_autoloader):
#     try:
#         return path_or_autoloader.path
#     except AttributeError:
#         assert type(path_or_autoloader) is str,\
#             "beard_path is not a str or an AutoLoader!"
#         return path_or_autoloader


# def get_literal_beard_paths(beard_paths):
#     return [get_literal_path(x) for x in beard_paths]


# def all_possible_beards(paths):
#     literal_paths = get_literal_beard_paths(paths)

#     for path in literal_paths:
#         for f in os.listdir(path):
#             if is_module(os.path.join(path, f)):
#                 yield os.path.basename(f)


def delegator_beard_gen(beards):
    for beard in beards:
        if hasattr(beard, "on_callback_query"):
            yield include_callback_query_chat_id(pave_event_space())(
                    per_chat_id(), create_open, beard, timeout=beard._timeout)
        else:
            yield pave_event_space()(
                per_chat_id(), create_open, beard, timeout=beard._timeout)


def main(config):

    # if pyconfig.get('start_server'):
    #     from skybeard import server

    if config.beards == "all":
        beards_to_load = all_possible_beards(config.beard_paths)
    else:
        beards_to_load = config.beards

    # Not sure importing is for the best
    for beard_path, possible_beard in itertools.product(
            config.beard_paths, beards_to_load):

        with PythonPathContext(get_literal_path(beard_path)):
            try:
                importlib.import_module(possible_beard+".setup_beard")
            except ImportError as ex:
                # If the module named by possible_beard does not exist, pass.
                #
                # If the module named by possible_beard does exist, but
                # .setup_beard does not exist, the module is imported anyway.
                pass

    # Check if all expected beards were imported.
    #
    # NOTE: This does not check for beards, only that the modules specified in
    # config.beards have been imported.
    for beard_name in beards_to_load:
        try:
            importlib.import_module(beard_name)
        except ImportError as e:
            logging.error("{} was not imported! Check your config.".format(
                beard_name))
            raise e

    # Check if there are any duplicate commands
    all_cmds = set()
    for beard in Beard.beards:
        if hasattr(beard, '__commands__'):
            for cmd in beard.__commands__:
                if isinstance(cmd, SlashCommand):
                    if cmd.cmd in (x.cmd for x in all_cmds):
                        # TODO Tell the user which beards conflict
                        raise DuplicateCommand(
                            "The command /{} occurs in more than "
                            "one beard.".format(cmd.cmd))
                    all_cmds.add(cmd)

    bot = telepot.aio.DelegatorBot(
        pyconfig.get('key'),
        list(delegator_beard_gen(Beard.beards))
    )

    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())

    if pyconfig.get('start_server'):
        from skybeard.server import app

        handler = app.make_handler()
        f = loop.create_server(handler, '0.0.0.0', 8080)
        srv = loop.run_until_complete(f)
        print('serving on', srv.sockets[0].getsockname())

    try:
        print('Listening ...')
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if pyconfig.get('start_server'):
            srv.close()
            loop.run_until_complete(srv.wait_closed())
            loop.run_until_complete(app.shutdown())
            loop.run_until_complete(handler.shutdown(60.0))
            loop.run_until_complete(app.cleanup())
        loop.close()

    # print('Listening ...')

    # loop.run_forever()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skybeard hails you!')

    parser.add_argument('-k', '--key', default=os.environ.get('TG_BOT_TOKEN'))
    parser.add_argument('--no-help', action='store_true')
    parser.add_argument('-d', '--debug', action='store_const', dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--start-server', action='store_const', const=True,
                        default=False)
    parser.add_argument('--no-auto-pip', action='store_const', const=True,
                        default=False)
    parser.add_argument('--auto-pip-upgrade', action='store_const', const=True,
                        default=False)

    parsed = parser.parse_args()

    pyconfig.set('start_server', parsed.start_server)
    pyconfig.set('no_auto_pip', parsed.no_auto_pip)
    pyconfig.set('auto_pip_upgrade', parsed.auto_pip_upgrade)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=parsed.loglevel)

    # Set up the master beard
    # TODO consider making this not a parrt of the BeardChatHandler class now
    # that we use pyconfig.
    BeardChatHandler.setup_beards(parsed.key, config.db_url)

    # If the user does not specially request --no-help, set up help command.
    if not parsed.no_help:
        create_help(config)

    logger.debug("Config found to be: {}".format(dir(config)))

    # TODO make an argparse here to override the config file (and also specify
    # the config file)
    main(config)

# bot = telepot.aio.DelegatorBot(TOKEN, [
#     include_callback_query_chat_id(
#         pave_event_space())(
#             per_chat_id(types=['private']), create_open, Lover, timeout=10),
# ])
