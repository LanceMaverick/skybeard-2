import tempfile
import subprocess as sp
import logging
import re
import telepot
import telepot.aio
from skybeard.beards import BeardAsyncChatHandlerMixin

logger = logging.getLogger(__name__)

class DebugBeard(telepot.aio.helper.ChatHandler, BeardAsyncChatHandlerMixin):

    # __init__ is implicit
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command("loadedbeards", self.loaded_beards)

    async def loaded_beards(self, msg):
        await self.sender.sendMessage(
            "Currently loaded beards are:\n\n{}".format(
                BeardAsyncChatHandlerMixin.beards))

    async def on_chat_message(self, msg):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage("DEBUG: I've recieved your message")
            await self.sender.sendMessage("DEBUG: {}".format(msg))

        await super().on_chat_message(msg)

    __userhelp__ = """I automatically print messages if the logger level is DEBUG.

/loadedbeards - Shows the currently loaded beards."""
