# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 15:56:52 2017

@author: David
"""
import re

import logging
import telepot
import telepot.aio
from skybeard.decorators import onerror
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate

class BasicAddition(BeardChatHandler):
    __userhelp__ = '''
    type /add (x,y) to add two numbers
    '''
    __commands__ = [
            ('add','addNumbers','Adds two numbers.')]
    
    @onerror
    async def addNumbers(self, msg):
        in_string = msg['text'].replace('/add ','')
        numbers = re.findall(r'([\d\.\-]+)', in_string)        
        
        ans = float(numbers[0])
        output_str = '{}'.format(numbers[0])
        for num in numbers[1:]:
            ans += float(num)
            output_str += '+ {}'.format(num)
        
        output_str += '= {}'.format(ans)                    
    
        await self.sender.sendMessage(output_str)