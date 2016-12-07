import logging
import telepot
from skybeard.beards import BeardChatHandler, Beard, create_command

logger = logging.getLogger(__name__)


# class DebugBeard(telepot.aio.helper.ChatHandler, BeardAsyncChatHandlerMixin):
class DebugBeard(BeardChatHandler):

    commands = [
        create_command('loadedbeards', 'loaded_beards')
    ]

    async def loaded_beards(self, msg):
        await self.sender.sendMessage(
            "Currently loaded beards are:\n\n{}".format(
                Beard.beards))

    async def on_chat_message(self, msg):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage("DEBUG: I've recieved your message")
            await self.sender.sendMessage("DEBUG: {}".format(msg))

        await super().on_chat_message(msg)

    __userhelp__ = """I automatically print messages if the logger level is DEBUG.

/loadedbeards - Shows the currently loaded beards."""
