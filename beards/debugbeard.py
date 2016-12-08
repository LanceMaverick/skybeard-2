import logging
from skybeard.beards import BeardChatHandler, Beard

logger = logging.getLogger(__name__)


class DebugBeard(BeardChatHandler):

    __commands__ = [
        ('loadedbeards', 'loaded_beards', "Shows the currently loaded beards."),
        ('debug', 'enter_debug', "Enters a debug trace in the terminal running the bot."),
    ]

    async def loaded_beards(self, msg):
        await self.sender.sendMessage(
            "Currently loaded beards are:\n\n{}".format(
                Beard.beards))

    async def enter_debug(self, msg):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage(
                "Entering debug trace mode in terminal.\n"
                "\nWARNING I will stop responding while debugging.")
            import pdb; pdb.set_trace()
            await self.sender.sendMessage("Left debug trace mode in terminal.")
        else:
            await self.sender.sendMessage(
                "Please run this bot with `-d` on "
                "the command line to enable this option.",
                parse_mode='Markdown')

    async def on_chat_message(self, msg):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage("DEBUG: I've recieved your message")
            await self.sender.sendMessage("DEBUG: {}".format(msg))

        await super().on_chat_message(msg)

    __userhelp__ = """I automatically print messages if the logger level is DEBUG.

/loadedbeards - Shows the currently loaded beards.
/debug - Enters a debug trace in the terminal running the bot."""
