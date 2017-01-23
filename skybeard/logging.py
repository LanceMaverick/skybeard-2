import asyncio
import logging


class TelegramHandler(logging.Handler):
    """A logging handler that posts directly to telegram"""

    def __init__(self, bot, parse_mode=None):
        self.bot = bot
        self.parse_mode = parse_mode
        super().__init__()

    def emit(self, record):
        coro = self.bot.sender.sendMessage(
            self.format(record), parse_mode=self.parse_mode)
        asyncio.ensure_future(coro)
