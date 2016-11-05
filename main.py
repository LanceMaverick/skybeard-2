#!/usr/bin/env python

from skybeard.plugins import Plugin

def main():
    updater = Plugin.updater
    updater.start_polling()
    updater.idle()

if __name__ == '___main__':
    main()



