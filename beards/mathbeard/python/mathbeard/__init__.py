# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 15:56:52 2017

@author: David Amison
"""
import sympy as sp

import telepot
import telepot.aio
from skybeard.decorators import onerror
from skybeard.utils import get_args
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate

class Calculator(BeardChatHandler):
    __userhelp__ = '''
    A calculator for doing numerical mathematics (not algebraic)
    
    Functions:
        
    /calc 'equation'    Calculates the answer to the equation input. The answer
                is output based on the current format chosen and can be changed
                using the /settings function
    '''
    
    __commands__ = [
            ('calc','calculate','Performs a calculation')]
    
    @onerror
    async def calculate(self, msg):
        
        #extract the equation input by the user
        equation = get_args(msg, return_string = True)
        
        await self.sender.sendMessage(equation)
        
        #solve the equation
        eq = sp.sympify(equation)   
        result = eq.evalf(10)
        
        
        await self.sender.sendMessage(result)