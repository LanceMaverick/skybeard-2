import logging
import requests
import json
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from skybeard.decorators import onerror
from skybeard.utils import partition_text, getMe
from .config import server_url, credentials, filter_words

logger = logging.getLogger(__name__)

class WillBeard(BeardChatHandler):
    __userhelp__ = """
    any message that starts with 'skybeard, ' will be sent to the W.I.L.L
    personal assistant as a query"""

    bot_name = await getMe()['first_name']
    __commands__ = [
            (
                #match any message that starts with "skybeard, "
                regex_predicate('(?i)^{}\,\s'.format(bot_name),
                'query_will',
                'queries the W.I.L.L assistant')
            ]

    @onerror
    async def query_will(self, msg):
        query_text = msg['text'].split(', ', 1)[1]
        if any(w in query_text.lower() for w in filter_words):
            await self.sender.sendMessage("I'm not comfortable googling that...")
            return
        response = requests.post(
                url="{0}/api/start_session".format(server_url),
                data=credentials).json()

        logger.debug(response)

        try:
            session_id = response["data"]["session_id"]
        except KeyError as e:
            logger.error(
                    'Request to W.I.L.L server failed.',
                    response, 
                    e)
            await self.sender.sendmessage(
                    'Sorry, there was an issue making the request.')
            return
        query_data = dict(
                session_id=session_id, 
                command=query_text)

        await self.sender.sendChatAction('typing')
        query_response = requests.post(
                url="{0}/api/command".format(server_url), 
                data=query_data).json()
        logger.debug(query_response)
        try:
            answer = query_response['text']
        except KeyError as e:
            logger.error('Request to W.I.L.L server failed.',
                    query_response,
                    e)
            await self.sender.sendmessage(
                    'Sorry, there was an issue trying to find an answer.')
            return

        if not answer:
            await self.sender.sendmessage('Sorry, I have no idea.')
            return
        
        for a in partition_text(answer):
            await self.sender.sendMessage(a)
        
        requests.post(
                url="{0}/api/end_session".format(server_url), 
                data={"session_id": session_id})
#
#    def on_close(self, e):
#        try:
#            requests.post(
#                    url="{0}/api/end_session".format(server_url), 
#                    data={"session_id": self.session_id})
#        except AttributeError:
#            #if no self.session_id, no worries.   
#            pass
#        super().no_close(e)


