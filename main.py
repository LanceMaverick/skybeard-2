#!/usr/bin/env python
import os
import sys
import logging
import importlib
import argparse

import config

from skybeard.beards import Beard
from skybeard.utils import (is_module,
                            get_literal_path,
                            get_literal_beard_paths,
                            all_possible_beards,
                            create_help)
import autoloaders

logger = logging.getLogger(__name__)


def main(config):
    for beard_path in config.beard_paths:
        sys.path.insert(0, get_literal_path(beard_path))

    logger.info("Loaded the following plugins:\n {}".format(
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

    updater = Beard.updater
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Skybeard hails you!')

    parser.add_argument('-k', '--key', default=os.environ.get('TG_BOT_TOKEN'))
    parser.add_argument('--no-help', action='store_true')
    parser.add_argument('-d', '--debug', action='store_const', dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)

    parsed = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=parsed.loglevel)


    # Set up the master beard
    Beard.setup_beard(parsed.key)

    # If the user does not specially request --no-help, set up help command.
    if not parsed.no_help:
        create_help(config)

    logger.debug("Config found to be: {}".format(dir(config)))


    # TODO make an argparse here to override the config file (and also specify
    # the config file)
    main(config)
