import os
import logging
import re
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from . import sentiment as sent
from . import config


class LoggerBeard(BeardChatHandler):

    def __init__(self, *args, **kwargs):
        self.curr_path = os.path.dirname(__file__)
        super().__init__(*args, **kwargs)
        self.register_command("saltreport", self.report)
        self.score_cmd = 'score'
        self.register_command(self.score_cmd, self.instant_report)
    
    async def on_chat_message(self, msg):
        #don't bother saving /score messages as they are likely not
        #representitive of chat
        if not msg['text'].startswith('/'+self.score_cmd):
            score = sent.analyze(msg)
            #responds message if a user sends a really negative message.
            #Set the cutoff for this in in config.py
            if score['compound']< config.cut:
                #await self.sender.sendMessage(
                #        'Are u ok {}?'.format(msg['from']['first_name']))

                #Uncomment to send a gif in the folder saved as "upset.gif".
                #For example: http://knowyourmeme.com/photos/481115-flying-lawnmower
                await self.sender.sendDocument((
                        'upset.gif', 
                        open(os.path.join(self.curr_path, 'upset.gif'),'rb' )))
            
            await sent.save(msg, score)
        await super().on_chat_message(msg)

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
        text = msg['text'].replace(
                '/'+self.score_cmd,
                '')
        score = sent.analyze(text)
        reply = '*Message:*\n**{}**\n*Score:* \n{}'.format(
                text,
                str(score))
        await self.sender.sendMessage(reply, parse_mode = 'markdown')

    __userhelp__ = """
    Logging for sentiment analysis.
    Send report with /saltreport"""

