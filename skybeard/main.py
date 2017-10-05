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
import subprocess as sp

import yaml
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

# import config


logger = logging.getLogger(__name__)


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


def find_last_child(path):
    return Path(str(path).replace(str(path.parent)+"/", ""))


def load_stache(stache_name, possible_dirs):
    for dir_ in possible_dirs:
        path = Path(dir_).resolve()
        python_path = path.parent
        with PythonPathContext(str(python_path)):
            stache_path = find_last_child(path) / stache_name
            stache_module = "{}.{}".format(str(find_last_child(path)), stache_name)
            module_spec = importlib.util.spec_from_file_location(
                    stache_module,
                    "{}.py".format(stache_path))

            if module_spec:
                foo = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(foo)

                return

    raise Exception("No stache with name {} found".format(stache_name))


def load_beard(beard_name, possible_dirs):
    for beard_path in possible_dirs:
        full_python_path = Path(get_literal_path(beard_path)).resolve()
        full_setup_beard_path = str(
            full_python_path / beard_name / "setup_beard.py")
        module_name = beard_name+".setup_beard"

        logger.debug("Attempting to import {} in file {}".format(
            module_name, full_python_path))

        with PythonPathContext(str(full_python_path)):
            try:
                module_spec = importlib.util.find_spec(
                    module_name,
                    full_setup_beard_path)
            except ImportError:
                # module_name is some_beard.setup_beard which means find_spec
                # automatically imports some_beard when it tries to find the
                # spec. If this fails, then just set module_spec to None (so it
                # is as if find_spec has found nothing).
                module_spec = None

        logger.debug("Got spec: {}".format(module_spec))

        if module_spec:
            # if find_spec finds a module, subsequent calls with the same
            # module name finds the already found module.
            logger.debug("Breaking loop")
            break
    else:
        # Try the old way
        logger.warning("Attempting to import {} as an old style beard. Old beards will eventually be deprecated.".format(beard_name))
        for beard_path in possible_dirs:
            try:
                with PythonPathContext(str(beard_path)):
                    module = importlib.import_module(beard_name)
            except ImportError:
                pass

        # TODO make this a much better exception
        try:
            logger.debug("Got module: {}".format(module))
        except UnboundLocalError:
            raise Exception("No beard found! Looked in: {}. Trying to find: {}".format(possible_dirs, beard_name))

        # This is a little hacky (TODO fix this!) but here goes:
        #
        # Basically, if there is an old style beard, then module is defined. If
        # not, then it's new style beard time, so import is needed.
    try:
        assert module
    except NameError:
        foo = importlib.util.module_from_spec(module_spec)
        with PythonPathContext(str(Path(module_spec.origin).parent.parent)):
            module_spec.loader.exec_module(foo)


def main():
    if pyconfig.get('beards') == "all":
        beards_to_load = all_possible_beards(pyconfig.get('beard_paths'))
    else:
        beards_to_load = pyconfig.get('beards', [])

    #########################
    # Alpha beard 3.0 stuff #
    #########################

    # First, pip install everyyyything that needs it
    for package in pyconfig.get('pip_installs', []):
        sp.check_call([
            'pip',
            'install',
            '-e',
            package
        ])

    # Now that a load of beards have potentially been installed, we need to
    # invalidate the caches so that they can be found by importlib.
    #
    # TODO: Except this doesn't work right now...
    importlib.invalidate_caches()

    # NOTE: loading beards as modules is currently in alpha
    #
    # It would be nice to one day only import beards this way. So much less
    # code to maintain.
    failed_imports = []
    for beard_module in pyconfig.get('beards_as_modules', []):
        try:
            importlib.import_module(beard_module)
        except ImportError:
            failed_imports.append(beard_module)

    if failed_imports:
        raise ImportError("Failed to import {}. Try rerunning skybeard.".format(failed_imports))

    #############################
    # End alpha beard 3.0 stuff #
    #############################

    for stache in pyconfig.get('staches', []):
        load_stache(stache, pyconfig.get('stache_paths', []))

    for possible_beard in beards_to_load:
    # If possible, import the beard through setup_beard.py
        load_beard(possible_beard, pyconfig.get('beard_paths'))

        # TODO support old style beards?

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

    if pyconfig.get('dry_run'):
        logger.info(
            "Dry run successful! Exciting normally before getting the loop...")

        # This needs to be done manually as telepot expects you to run the bot
        telepot.aio.api._pools['default'].close()

        logger.info("So long, and thanks for all the fish!")
        return

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
        f = loop.create_server(handler, pyconfig.get('host'), pyconfig.get('port'))
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


# if __name__ == '__main__':
def if__name____main__():
    parser = argparse.ArgumentParser(description='Skybeard hails you!')

    parser.add_argument('-k', '--key', default=os.environ.get('TG_BOT_TOKEN'))
    parser.add_argument('-c', '--config-file',
                        default=(os.environ.get('SKYBEARD_CONFIG')))
    parser.add_argument('--no-help', action='store_true')
    parser.add_argument('-d', '--debug', action='store_const', dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--start-server', action='store_const', const=True,
                        default=False)
    parser.add_argument('--no-auto-pip', action='store_const', const=True,
                        default=False)
    parser.add_argument('--beards', nargs='+', default=None)
    parser.add_argument('--beards-as-modules', nargs='+', default=None)
    parser.add_argument('--pip-installs', nargs='+', default=None)
    parser.add_argument('--auto-pip-upgrade', action='store_const', const=True,
                        default=False)
    parser.add_argument('--dry-run', action='store_const', const=True,
                        default=False)

    parsed = parser.parse_args()

    if parsed.config_file:
        pyconfig.set('config_file', os.path.abspath(parsed.config_file))

    # Load predefined defaults
    default_config_path = os.path.join(
        os.path.dirname(__file__),
        'default_config.yml'
    )
    with open(default_config_path) as default_config_file:
        for k, v in yaml.load(default_config_file).items():
            pyconfig.set(k, v)

    # If there is a config file, load it and put it into pyconfig
    if pyconfig.get('config_file'):
        with open(pyconfig.get('config_file')) as config_file:
            for k, v in yaml.load(config_file).items():
                pyconfig.set(k, v)

    if parsed.beards:
        pyconfig.set('beards', parsed.beards)
    elif not pyconfig.get('beards'):
        pyconfig.set('beards', [])
    if parsed.beards_as_modules:
        pyconfig.set('beards_as_modules', parsed.beards_as_modules)
    beard_paths = pyconfig.get('beard_paths', [])
    pyconfig.set('beard_paths', [os.path.expanduser(x) for x in beard_paths])
    stache_paths = pyconfig.get('stache_paths', [])
    pyconfig.set('stache_paths', [os.path.expanduser(x) for x in stache_paths])

    pyconfig.set('loglevel', parsed.loglevel)
    pyconfig.set('start_server', parsed.start_server)
    pyconfig.set('no_auto_pip', parsed.no_auto_pip)
    pyconfig.set('auto_pip_upgrade', parsed.auto_pip_upgrade)
    # If there's something on the command line, replace the config value
    if parsed.pip_installs:
        pyconfig.set('pip_installs', parsed.pip_installs)
    pyconfig.set('admins', [a[1] for a in pyconfig.get('admins', [])])
    print(pyconfig.get('admins'))
    pyconfig.set('dry_run', parsed.dry_run)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=pyconfig.get('loglevel'))

    logger = logging.getLogger(__name__)

    # Set up the master beard
    # TODO consider making this not a parrt of the BeardChatHandler class now
    # that we use pyconfig.
    BeardChatHandler.setup_beards(parsed.key, pyconfig.get('db_url'))
    # pyconfig.set('db_url', config.db_url)
    # pyconfig.set('db_bin_path', config.db_bin_path)
    if not os.path.exists(pyconfig.get('db_bin_path')):
        os.mkdir(pyconfig.get('db_bin_path'))

    # If the user does not specially request --no-help, set up help command.
    if not parsed.no_help:
        create_help()

    # logger.debug("Config found to be: {}".format(dir(config)))

    # TODO make an argparse here to override the config file (and also specify
    # the config file)
    main()

# bot = telepot.aio.DelegatorBot(TOKEN, [
#     include_callback_query_chat_id(
#         pave_event_space())(
#             per_chat_id(types=['private']), create_open, Lover, timeout=10),
# ])
