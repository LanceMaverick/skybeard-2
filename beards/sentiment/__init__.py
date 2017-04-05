import os
import logging
import re
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import Filters
from skybeard.decorators import onerror
from skybeard.server import web
from skybeard.api.database import is_key_match
from . import sentiment as sent
from . import config


class SentBeard(BeardChatHandler):
    __commands__ = [
           ('saltreport', 'report', 'Sends a detailed summary of the scores so far'),
           ('mysalt', 'user_report', 'Sends a distribution of your scores'),
           ('score', 'instant_report', 'Sends you the score of that text. Score not logged'),
           (Filters.text_no_cmd, 'log_message_score', 'scores incoming text messages'),
            ]
    __userhelp__ = """
    Logging for sentiment analysis.
   """ 
#    __routes__ = [('/sentData', 'http_get_sents', 'get'),]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
    async def log_message_score(self, msg):
        score = sent.analyze(msg)
        #responds message if a user sends a really negative message.
        #Set the cutoff for this in in config.py
        if score['compound']< config.cut:

            #Uncomment to send a gif in the folder saved as "upset.gif".
            #For example: http://knowyourmeme.com/photos/481115-flying-lawnmower
            curr_path = os.path.dirname(__file__)
            try:
                await self.sender.sendDocument((
                        'upset.gif', 
                        open(
                            os.path.join(curr_path, 'upset.gif'),'rb' )))
            except FileNotFoundError:
                await self.sender.sendMessage(
                        '{}, there is no need to be upset'.format(
                            msg['from']['first_name']))
        
        await sent.save(msg, score)
    @onerror
    async def report(self, msg):
        await self.sender.sendMessage('Generating report for the last 1000 messages...')
        await self.sender.sendChatAction('upload_photo')
        plot1, plot2, plot3, plot4 = sent.get_results(msg, neut= False)
        await self.sender.sendPhoto((
                'sentiment1.png', plot1)) 
        await self.sender.sendPhoto((
                'sentiment2.png', plot2)) 
        await self.sender.sendPhoto((
                'sentiment3.png', plot3)) 
#        await self.sender.sendPhoto((
#                'sentiment4.png', plot4)) 

    async def user_report(self, msg):
        plot = sent.get_user_results(msg, neut= False)
        await self.sender.sendPhoto((
            'sentimentuser.png', plot))
    
    async def instant_report(self, msg):
        text = msg['text'].replace('/score', '')
        score = sent.analyze(text)
        reply = '*Message:*\n**{}**\n*Score:* \n{}'.format(
                text,
                str(score))
        await self.sender.sendMessage(reply, parse_mode = 'markdown')

    
    async def http_get_sents(request):
        data = request.rel_url.query
        data = dict(data)
        if not is_key_match(data['key']):
            return web.json_response({'status': 'ERROR: Not authenticated'})
        elif 'chat_id' not in data:
            return web.json_response({'status': 'No chat id specified'})
        else:

            data.pop('key')
            sent_data = sent.get_raw_data(**data)
            response = dict(chat_id = data['chat_id'], results = [row for row in sent_data])
            return web.json_response(response)

            


            





