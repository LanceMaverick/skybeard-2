import os
import logging
import re
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler, Filters
from . import sentiment as sent
from . import config


class LoggerBeard(BeardChatHandler):
    __commands__ = [
           ('saltreport', 'report', 'Sends a detailed summary of the scores so far'),
           ('score', 'instant_report', 'Sends you the score of that text. Score not logged'),
           (Filters.text, 'log_message_score', 'scores incoming text messages'),
            ]
    __userhelp__ = """
    Logging for sentiment analysis.
    Send report with /saltreport"""
    
    async def log_message_score(self, msg):
        #don't bother saving /score messages as they are likely not
        #representitive of chat

        if not msg['text'].startswith('/score'):
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

    async def report(self, msg):
        plot1, plot2, plot3, plot4 = sent.get_results(msg)
        await self.sender.sendPhoto((
                'sentiment1.png', plot1)) 
        await self.sender.sendPhoto((
                'sentiment2.png', plot2)) 
        await self.sender.sendPhoto((
                'sentiment3.png', plot3)) 
#        await self.sender.sendPhoto((
#                'sentiment4.png', plot4)) 
    
    async def instant_report(self, msg):
        text = msg['text'].replace('/score', '')
        score = sent.analyze(text)
        reply = '*Message:*\n**{}**\n*Score:* \n{}'.format(
                text,
                str(score))
        await self.sender.sendMessage(reply, parse_mode = 'markdown')


