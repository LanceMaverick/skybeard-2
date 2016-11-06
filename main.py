#!/usr/bin/env python
import os
import sys
import logging
import importlib
import configparser
import argparse

from skybeard.beards import Beard
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def is_module(filename):
    fname, ext = os.path.splitext(filename)
    if ext == ".py":
        return True
    elif os.path.exists(os.path.join(filename, "__init__.py")):
        return True
    else:
        return False

def all_possible_beards(paths):
    for path in paths:
        for f in os.listdir(path):
            if is_module(os.path.join(path, f)):
                yield os.path.basename(f)


def main(config):
    beard_path = "beards/"
    sys.path.insert(0, beard_path)

    logger.debug("Available plugins: {}".format(
        list(all_possible_beards([beard_path]))))
    logger.debug("Config.main.beards: {}".format(config["main"]["beards"]))
    requested_beards = config["main"]["beards"].split("\n")

    # Remove empty firstline if needed
    if requested_beards[0] == "":
        requested_beards = requested_beards[1:]

    if requested_beards == ["all"]:
        for beard_name in all_possible_beards([beard_path]):
            importlib.import_module(beard_name)
    else:
        for beard_name in requested_beards:
            importlib.import_module(beard_name)

    sys.path.pop(0)

    updater = Beard.updater
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skybeard hails you!')

    parser.add_argument('-c', '--config-file', default="config.ini")
    parser.add_argument('-k', '--key', default=os.environ.get('TG_BOT_TOKEN'))

    parsed = parser.parse_args()

    # Set up the master beard
    Beard.setup_beard(parsed.key)

    logger.debug("Getting config")
    config = configparser.ConfigParser()
    config.read(parsed.config_file)
    logger.debug("Config found to be: {}".format(config))


    # TODO make an argparse here to override the config file (and also specify
    # the config file)
    main(config)
