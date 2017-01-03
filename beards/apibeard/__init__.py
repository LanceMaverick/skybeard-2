from multiprocessing import Process
import logging

from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror

from . import server


logger = logging.getLogger(__name__)


class APIBeard(BeardChatHandler):

    __userhelp__ = "A simple api beard that runs a flask server"
    __commands__ = [
        ('restartserver', 'restart_server', 'Restarts flask server.'),
        ('whoami', 'who_am_i', 'Returns the chat id for current chat.')
    ]

    async def who_am_i(self, msg):
        await self.sender.sendMessage("Current chat_id: "+str(self.chat_id))

    sanic_proc = Process(target=server.start_app, args=(None,))

    @classmethod
    def _restart_server(cls):
        pass

    @onerror
    async def restart_server(self, msg):
        await self.logger.debug("Server: "+str(APIBeard.sanic_proc))
        return self._restart_server()


APIBeard.sanic_proc.start()
