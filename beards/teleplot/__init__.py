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
      eq_parser = TelePlot.eqn_parser 
      options = re.findall(r'\-(\w+)\s\"([\w\d\s\.\-\'\)\(\,]+)', in_string)
      
      print("options: ")
      print(options)
      if len(arrays) < 1:
        Y = []
        X = linspace(-10, 10, 100)
        opts2perform = TelePlot.checkandParse(in_string)
        print(opts2perform)
        if len(opts2perform) == 0:
         eqn = re.findall(r'(\([\w\(\)\d\s\-\+\*\/]+\))', in_string)
         eqn = eqn[0]
         for i in X:
          equation = eqn.replace('x','{}'.format(i)).replace('(','').replace(')','')
          j = sp.simplify(equation) 
          Y.append(j)
        else:
         strings_for_y = []
         for i in X:
          final_string = in_string[1:-1]
          for key in opts2perform:
            inside = sp.simplify(opts2perform[key][1].replace('x','{}'.format(i)))
            operation = eq_parser[key](inside)
            final_string = final_string.replace('{}({})'.format(opts2perform[key][0], opts2perform[key][1]), '{}'.format(operation))
          strings_for_y.append(final_string)
         for y in strings_for_y:
            j = sp.simplify(y)
            Y.append(j)

      else:
        print("Arrays: ")
        assert len(arrays) == 2, "Error: Insufficient Number of Arrays Given."
        X = re.findall(r'([\d\.\-]+)', arrays[0])
        Y = re.findall(r'([\d\.\-]+)', arrays[1])
        print(X,Y) 
    
      plotter = TelePlot.TelePlot(X, Y)
      file_name = plotter.parseOpts(options)
      await self.sender.sendPhoto(('temp.png', open('{}'.format(file_name), 'rb')))
      os.remove('{}'.format(file_name))
