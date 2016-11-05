#!/usr/bin/env python
import os
import sys
import logging
import importlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from skybeard.plugins import Plugin

PATH = "plugins/"
sys.path.insert(0, PATH)

logger.debug("os.listdir({}) = {}".format(PATH, os.listdir(PATH)))
for f in os.listdir(PATH):
    fname, ext = os.path.splitext(f)
    importlib.import_module(fname)
sys.path.pop(0)


def main():
    updater = Plugin.updater
    updater.start_polling()
    updater.idle()

if __name__ == '___main__':
    main()
