#!/usr/bin/env python
import os
import asyncio
import sys
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
                            all_possible_beards)
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

    if pyconfig.get('start_server'):
        from skybeard import server

    if config.beards == "all":
        beards_to_load = all_possible_beards(config.beard_paths)
    else:
        beards_to_load = config.beards

    # Not sure importing is for the best
    for beard_path, possible_beard in itertools.product(
            config.beard_paths, beards_to_load):

        try:
            sys.path.insert(0, get_literal_path(beard_path))
            importlib.import_module(possible_beard+".setup_beard")
        except ImportError as ex:
            # If the module does not exist, pass. If the module exists, but
            # setup_beard does not exist, the module is imported anyway
            #
            # TODO Say something if a beard is specified in config.beard, but
            # never imported
            pass
        finally:
            sys.path.pop(0)



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

    if pyconfig.get('start_server'):
        asyncio.ensure_future(server.start())

    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())
    print('Listening ...')

    loop.run_forever()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skybeard hails you!')

    parser.add_argument('-k', '--key', default=os.environ.get('TG_BOT_TOKEN'))
    parser.add_argument('--no-help', action='store_true')
    parser.add_argument('-d', '--debug', action='store_const', dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--start-server', action='store_const', const=True, default=False)

    parsed = parser.parse_args()

    pyconfig.set('start_server', parsed.start_server)

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
