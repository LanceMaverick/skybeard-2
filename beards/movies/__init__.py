from telegram.ext import CommandHandler
from skybeard.beards import Beard
from . import movies

class Movies(Beard):
    
    def initialise(self):
        self.disp.add_handler(CommandHandler('movie', self.movie_search))

    def movie_search(self, bot, update):
        movie_title = update.message.text.split('/movie',1)[1]
        if not movie_title:
            update.message.reply_text('please specify a movie title')
        else:
            movies.search(update.message, movie_title)


