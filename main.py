#!/usr/bin/env python
import os
import asyncio
import sys
import logging
import importlib
import argparse

import telepot
from telepot.aio.delegate import (per_chat_id,
                                  create_open,
                                  pave_event_space,
                                  include_callback_query_chat_id)

logger = logging.getLogger(__name__)

from skybeard.beards import Beard, BeardChatHandler, SlashCommand
from skybeard.help import create_help
import config

class DuplicateCommand(Exception):
    pass


def is_module(filename):
    fname, ext = os.path.splitext(filename)
    if ext == ".py":
        return True
    elif os.path.exists(os.path.join(filename, "__init__.py")):
        return True
    else:
        return False


def get_literal_path(path_or_autoloader):
    try:
        return path_or_autoloader.path
    except AttributeError:
        assert type(path_or_autoloader) is str,\
            "beard_path is not a str or an AutoLoader!"
        return path_or_autoloader


def get_literal_beard_paths(beard_paths):
    return [get_literal_path(x) for x in beard_paths]


def all_possible_beards(paths):
    literal_paths = get_literal_beard_paths(paths)

    for path in literal_paths:
        for f in os.listdir(path):
            if is_module(os.path.join(path, f)):
                yield os.path.basename(f)


def delegator_beard_gen(beards):
    for beard in beards:
        if hasattr(beard, "on_callback_query"):
            yield include_callback_query_chat_id(pave_event_space())(
                    per_chat_id(), create_open, beard, timeout=beard._timeout)
        else:
            yield pave_event_space()(
                per_chat_id(), create_open, beard, timeout=beard._timeout)


def main(config):
    for beard_path in config.beard_paths:
        sys.path.insert(0, get_literal_path(beard_path))

    logger.info("The following plugins were found:\n {}".format(
        ', '.join(list(all_possible_beards(config.beard_paths)))))
    logger.info("config.beards: {}".format(config.beards))

    if config.beards == "all":
        for beard_name in all_possible_beards(config.beard_paths):
            importlib.import_module(beard_name)
    else:
        for beard_name in config.beards:
            importlib.import_module(beard_name)

    for beard_path in config.beard_paths:
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
        BeardChatHandler.key,
        list(delegator_beard_gen(Beard.beards))
    )

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

    parsed = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=parsed.loglevel)

    # Set up the master beard
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
