import logging
import telepot
import telepot.aio
from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)

class CallbackTestBeard(BeardChatHandler):
    '''Simple callback button example for skybeard-2
    Type /callbackstart to begin.
    '''
    _timeout = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command('callbackstart', self.start)

        self.keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Option 1', callback_data='1'),
                 InlineKeyboardButton(text='Option 2', callback_data='2')],
                [InlineKeyboardButton(text='Option 3', callback_data='3')],
            ])

    __userhelp__ = '''/callbackstart to test callbacks.'''

    async def start(self, msg):
        await self.sender.sendMessage('Please choose:',
                                      reply_markup=self.keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        await self.bot.editMessageText(
            telepot.origin_identifier(msg),
            text="Selected option: {}".format(query_data),
            reply_markup=self.keyboard)
