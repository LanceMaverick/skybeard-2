# from telegram.ext import CommandHandler, MessageHandler, Filters
import telepot
import telepot.aio
from skybeard.beards import BeardAsyncChatHandlerMixin
from . import config, steam, overwatch

class Steam(telepot.aio.helper.ChatHandler, BeardAsyncChatHandlerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command('gamenews', self.game_news)

    async def game_news(self, msg):
        game_list = list(config.game_ids.keys())
        text = msg['text']
        game_list_str = '\n'.join(game_list)
        try:
            game = text.split('/gamenews',1)[1].strip()
        except IndexError:
            await self.sender.sendMessage(
                    'Please specify a steam game:\n'+game_list_str)
            return
        if game == 'overwatch':
            # overwatch.post_news(bot, update)
            await self.sender.sendMessage("Sorry, working on it!")
        elif game not in game_list:
            await self.sender.sendMessage(
                    'Game not recognised. Please specify a steam game:\n'+game_list_str)
        else:
            game_id = config.game_ids[game]
            await self.sender.sendMessage("Sorry, working on it!")
            # steam.post_news(bot, update, game_id)
