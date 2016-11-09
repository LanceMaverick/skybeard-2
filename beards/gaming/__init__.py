from telegram.ext import CommandHandler, MessageHandler, Filters
from skybeard.beards import Beard
from . import config, steam, overwatch

class Steam(Beard):
    def initialise(self):
        self.disp.add_handler(CommandHandler('gamenews', self.game_news))

    def game_news(self, bot, update):
        game_list = list(config.game_ids.keys())
        text = update.message.text
        game_list_str = '\n'.join(game_list)
        try:
            game = text.split('/gamenews',1)[1].strip()
        except IndexError:
            update.message.reply_text(
                    'Please specify a steam game:\n'+game_list_str, 
                    quote= False)
            return
        if game == 'overwatch':
            overwatch.post_news(bot, update)
        elif game not in game_list:
            update.message.reply_text(
                    'Game not recognised. Please specify a steam game:\n'+game_list_str, 
                    quote= False)
        else:
            game_id = config.game_ids[game]
            steam.post_news(bot, update, game_id)

                
                

