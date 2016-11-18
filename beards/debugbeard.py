import tempfile
import subprocess as sp
import logging
import re

import telepot
import telepot.aio
from skybeard.beards import BeardMixin, BeardLoader

logger = logging.getLogger(__name__)

class DebugBeard(telepot.aio.helper.ChatHandler, BeardMixin):

    # __init__ is implicit

    async def on_chat_message(self, msg):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage("DEBUG: I've recieved your message")
            await self.sender.sendMessage("DEBUG: {}".format(msg))

        try:
            text = msg['text']
        except KeyError:
            return

        if re.match("^/loadedbeards.*", text):
            await self.sender.sendMessage("Currently loaded beards are:\n\n{}".format(BeardMixin.beards))

    __userhelp__ = """I automatically print messages if the logger level is DEBUG.

/loadedbeards - Shows the currently loaded beards."""
