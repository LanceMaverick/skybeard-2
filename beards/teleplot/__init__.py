#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from skybeard.decorators import onerror
from skybeard.utils import get_args
from . import TelePlot
import re
import os
import sympy as sp
from numpy import linspace
from math import *

def format_msg(msg):
    text = msg['text']
    return ' '.join(get_args(text)).title()


class NationalRailDepartures(BeardChatHandler):
    __userhelp__ = """
    The following commands are available:
     """

    __commands__ = [
        ("teleplot", "makePlot", "Make plot from two arrays.\n`\\teleplot [x1,x2,..,xN] [y1,y2,..,yN]`\n`\\teleplot (x**2+2*x+3)`\nAdditional options: `-xaxis \"label\"`, `-yaxis \"label\"`\n Currently only index, add, subtract, divide, multiply available for equation notation."),
    ]

    @onerror
    async def makePlot(self, msg):
      in_string = msg['text'].replace('/teleplot ', '')
      arrays = re.findall(r'(\[[\-\d\,\.\s]+\])+', in_string)
        
      options = re.findall(r'\-(\w+)\s\"([\w\d\s\.\-\'\)\(\,]+)', in_string)
      
      print("options: ")
      print(options)
      if len(arrays) < 1:
        eqn = re.findall(r'(\([\w\(\)\d\s\-\+\*\/]+\))', in_string)
        eqn = eqn[0]
        X = linspace(-10, 10, 100)
        Y = []
        for i in X:
         equation = eqn.replace('x','{}'.format(i)).replace('(','').replace(')','')
         j = sp.simplify(equation) 
         Y.append(j)

      else:
        print("Arrays: ")
        assert len(arrays) == 2, "Error: Insufficient Number of Arrays Given."
        X = re.findall(r'([\d\.\-]+)', arrays[0])
        Y = re.findall(r'([\d\.\-]+)', arrays[1])
        print(X,Y) 
      content_type, chat_type, chat_id = telepot.glance(msg)
    
      plotter = TelePlot.TelePlot(X, Y)
      file_name = plotter.parseOpts(options)
      await self.sender.sendPhoto(('temp.png', open('{}'.format(file_name), 'rb')))
      os.remove('{}'.format(file_name))
