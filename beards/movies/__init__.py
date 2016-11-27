# from telegram.ext import CommandHandler
import telepot
import telepot.aio
from urllib.request import urlopen
from skybeard.beards import BeardAsyncChatHandlerMixin
from . import movies

class Movies(telepot.aio.helper.ChatHandler, BeardAsyncChatHandlerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command('movie', self.movie_search)

    async def movie_search(self, msg):
        movie_title = msg['text'].split('/movie',1)[1].strip()
        if not movie_title:
            await self.sender.sendMessage('please specify a movie title')
        else:
            search = movies.search(movie_title)
            if search["photourl"] and search["photourl"]!='N/A':
                try:
                    await self.sender.sendPhoto(("poster.jpg", urlopen(search["photourl"])))
                except telepot.exception.TelegramError:
                    await self.sender.sendMessage(search["photourl"])
            await self.sender.sendMessage(search["text"])


