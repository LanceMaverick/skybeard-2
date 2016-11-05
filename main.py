#!/usr/bin/env python
import os
import sys
import logging
import importlib
import yaml
import argparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from skybeard.beards import Beard

def main(config):
    beard_path = "beards/"
    sys.path.insert(0, beard_path)

    logger.debug("os.listdir({}) = {}".format(beard_path,
                                              os.listdir(beard_path)))
    if config["beards"] == "all":
        for f in os.listdir(beard_path):
            fname, ext = os.path.splitext(f)
            importlib.import_module(fname)
    elif isinstance(config["beards"], list):
        for f in config["beards"]:
            fname, ext = os.path.splitext(f)
            importlib.import_module(fname)
    else:
        assert False, "Skybeard does not understand which beards to wear. Check your config file."


    sys.path.pop(0)

    updater = Beard.updater
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skybeard hails you!')

    parser.add_argument('-c', '--config-file', default="config.yaml")
    parser.add_argument('-k', '--key', default=os.environ.get('TG_BOT_TOKEN'))

    parsed = parser.parse_args()

    # Set up the master beard
    Beard.setup_beard(parsed.key)

    logger.debug("Getting config")
    config = yaml.load(open("config.yaml"))
    logger.debug("Config found to be: {}".format(config))


    # TODO make an argparse here to override the config file (and also specify
    # the config file)
    main(config)
