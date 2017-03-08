#!/usr/bin/env python
import argparse
import yaml
from pathlib import Path
import logging

import blessings

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Search for available beards to get with getbeard.py.')

    parser.add_argument('search_terms', nargs="+")
    parser.add_argument('-d', '--debug', action="store_true",
                        default=False)

    return parser.parse_args()


def get_cache_info():
    p = Path("beard_repo")

    yamls = p.glob("*.yml")

    cache_info = (yaml.load(x.open()) for x in yamls)

    return cache_info


def main():
    parsed = parse_arguments()
    if parsed.debug:
        logging.basicConfig(level=logging.DEBUG)

    cache = get_cache_info()

    def match(item, terms):
        for i in terms:
            if i in item['name']:
                logger.debug("{} found in {}".format(i, item['name']))
                return True
            elif item['description'] is not None and i in item['description']:
                logger.debug("{} found in {}".format(i, item['description']))
                return True

    matches = [x for x in cache if match(x, parsed.search_terms)]

    # Print it
    t = blessings.Terminal()

    for i in sorted(matches, key=lambda x: x['name']):
        line = "{name} : {description}".format(**i)
        for st in parsed.search_terms:
            line = line.replace(st, t.bold + st + t.normal)
        print(line)


if __name__ == '__main__':
    main()
