#!/usr/bin/env python

from skybeard.plugins import Plugin

# Should magically add it to the bot
from plugins.postcats import PostCats

def main():
    updater = Plugin.updater
    updater.start_polling()
    updater.idle()

if __name__ == '___main__':
    main()
