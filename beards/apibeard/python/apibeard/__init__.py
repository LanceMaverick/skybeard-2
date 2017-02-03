# from multiprocessing import Process

import sanic
assert sanic.__version__ == "0.1.7", "Due to reasons detailed in https://github.com/channelcat/sanic/issues/275, this app currently only supports Sanic version 0.1.7."

from .apibeard import APIBeard
