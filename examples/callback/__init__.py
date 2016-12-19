import logging

import telepot
import telepot.aio
from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, ThatsNotMineException


logger = logging.getLogger(__name__)

# Adapted from https://github.com/python-telegram-bot/python-telegram-bot/blob/46657afa95bd720bb1319fcb9bc1e8cae82e02b9/examples/inlinekeyboard.py
# And then adapted for telepot


class CallbackTestBeard(BeardChatHandler):
    '''Simple callback button example for skybeard-2

    Type /callbackstart to begin.

    '''

    _timeout = 10

    __commands__ = [
        ('callbackstart', 'start', 'Starts callback button test.')
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Option 1', callback_data=self.serialize('1')),
                 InlineKeyboardButton(
                     text='Option 2', callback_data=self.serialize('2'))],
                [InlineKeyboardButton(
                    text='Option 3', callback_data=self.serialize('3'))],
            ])

    __userhelp__ = """A callback test beard."""

    async def start(self, msg):
        await self.sender.sendMessage('Please choose:',
                                      reply_markup=self.keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
        except ThatsNotMineException:
            return

        await self.bot.editMessageText(
            telepot.origin_identifier(msg),
            text="Selected option: {}".format(data),
            reply_markup=self.keyboard)
