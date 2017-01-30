import logging
from skybeard.beards import BeardChatHandler, Beard
from skybeard.decorators import onerror

logger = logging.getLogger(__name__)


class DebugBeard(BeardChatHandler):

    __commands__ = [
        ('loadedbeards', 'loaded_beards', "Shows the currently loaded beards."),
        ('debug', 'enter_debug', "Enters a debug trace in the terminal running the bot."),
        ('except', 'except_on_purpose',
         "Raises generic exception in code (useful for testing.)"),
        ('getme', 'who_am_i', "Returns JSON for bot.getMe().")
    ]

    @onerror
    async def who_am_i(self, msg):
        await self.sender.sendMessage(str(await self.bot.getMe()))

    @onerror("I just excepted on purpose!")
    async def except_on_purpose(self, msg):
        raise Exception("Raising generic exception")

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
        self.logger.debug("I've recieved your message")
        self.logger.debug(msg)

        await super().on_chat_message(msg)

    __userhelp__ = "I automatically print messages if the logger level is DEBUG."
