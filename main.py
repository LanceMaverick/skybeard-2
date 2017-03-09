#!/usr/bin/env python
import os
import aiohttp
import asyncio
import logging
# import itertools
import importlib
# from importlib.util import find_spec
import argparse
import pyconfig
from pathlib import Path

import telepot
from telepot.aio.delegate import (per_chat_id,
                                  create_open,
                                  pave_event_space,
                                  include_callback_query_chat_id)
from skybeard.beards import Beard, BeardChatHandler, SlashCommand
from skybeard.help import create_help
from skybeard.utils import (get_literal_path,
                            all_possible_beards,
                            PythonPathContext)

import config


class DuplicateCommand(Exception):
    pass


def delegator_beard_gen(beards):
    for beard in beards:
        if hasattr(beard, "on_callback_query"):
            yield include_callback_query_chat_id(pave_event_space())(
                    per_chat_id(), create_open, beard, timeout=beard._timeout)
        else:
            yield pave_event_space()(
                per_chat_id(), create_open, beard, timeout=beard._timeout)


def load_beard(beard_name, possible_dirs):
    beard_specs = []
    for beard_path in possible_dirs:
        # with PythonPathContext(get_literal_path(beard_path)):
        full_path = Path(get_literal_path(beard_path)).resolve()
        full_setup_beard_path = str(full_path / beard_name / "setup_beard.py")
        logger.debug("Attempting to import {} in file {}".format(
            beard_name+".setup_beard", full_path))
        with PythonPathContext(str(full_path)):
            x = importlib.util.find_spec(
                beard_name+".setup_beard",
                # str(beard_path+beard_name).replace("/", "_"),
                full_setup_beard_path)
        logger.debug("Got spec: {}".format(x))
        if x:
            beard_specs.append(x)

            # if find_spec finds a module, subsequent calls with the same
            # module name only find the first thing of module
            logger.debug("Breaking loop")
            break
    else:
        raise Exception("No beard found!")

    # if len(beard_specs) == 0:
    #     raise Exception("No beard found!")
    if len(beard_specs) > 1:
        raise Exception(
            "There can only be one! Multiple beards with same name found.")
    else:
        spec = beard_specs[0]
        foo = importlib.util.module_from_spec(spec)
        with PythonPathContext(str(Path(spec.origin).parent.parent)):
            spec.loader.exec_module(foo)


def main(config):
    if config.beards == "all":
        beards_to_load = all_possible_beards(config.beard_paths)
    else:
        beards_to_load = config.beards

    # Not sure importing is for the best
    # for beard_path, possible_beard in itertools.product(
    #         config.beard_paths, beards_to_load):

    #     with PythonPathContext(get_literal_path(beard_path)):
    #         try:
    #             importlib.import_module(possible_beard+".setup_beard")
    #         except ImportError as ex:
    #             # If the module named by possible_beard does not exist, pass.
    #             #
    #             # If the module named by possible_beard does exist, but
    #             # .setup_beard does not exist, the module is imported anyway.
    #             pass
    #             # if importlib.import_module(possible_beard):
    #             #     pass
    #             # else:
    #             #     raise ex
    for possible_beard in beards_to_load:
        # If possible, import the beard through setup_beard.py
        load_beard(possible_beard, config.beard_paths)

        assert pyconfig.get('loglevel') == logger.getEffectiveLevel(), \
            "{} has caused the loglevel to be changed from {} to {}!".format(
                possible_beard,
                pyconfig.get('loglevel'),
                logger.getEffectiveLevel())

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

    async def bot_message_loop_and_aiothttp_session():
        async with aiohttp.ClientSession() as session:
            pyconfig.set('aiohttp_session', session)
            await bot.message_loop()

    # loop.create_task(bot.message_loop())
    loop.create_task(bot_message_loop_and_aiothttp_session())

    if pyconfig.get('start_server'):
        from skybeard.server import app
        # From https://github.com/aio-libs/aiohttp-cors
        #
        # Must be done after the beards are loaded.
        import aiohttp_cors
        # Configure default CORS settings.
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
        })

        # Configure CORS on all routes.
        for route in list(app.router.routes()):
            cors.add(route)

        handler = app.make_handler()
        f = loop.create_server(handler, config.host, config.port)
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

    pyconfig.set('loglevel', parsed.loglevel)
    pyconfig.set('start_server', parsed.start_server)
    pyconfig.set('no_auto_pip', parsed.no_auto_pip)
    pyconfig.set('auto_pip_upgrade', parsed.auto_pip_upgrade)
    pyconfig.set('admins', [a[1] for a in config.admins])
    print(pyconfig.get('admins'))

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=pyconfig.get('loglevel'))

    logger = logging.getLogger(__name__)

    # Set up the master beard
    # TODO consider making this not a parrt of the BeardChatHandler class now
    # that we use pyconfig.
    BeardChatHandler.setup_beards(parsed.key, config.db_url)
    pyconfig.set('db_url', config.db_url)
    pyconfig.set('db_bin_path', config.db_bin_path)
    if not os.path.exists(pyconfig.get('db_bin_path')):
        os.mkdir(pyconfig.get('db_bin_path'))

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
