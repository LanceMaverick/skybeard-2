import matplotlib.pyplot as plt
from uuid import uuid4
import mpmath as mt
import re

      
trig_dict = {'sin' : mt.sin, 'cos' : mt.cos, 'tan' : mt.tan,
             'asin' : mt.asin, 'acos' : mt.acos, 'atan' : mt.tan,
             'cosec' : mt.csc, 'sec' : mt.sec, 'cot' : mt.cot}
hyp_dict = {'sinh' : mt.sinh, 'cosh' : mt.cosh, 'tanh' : mt.tan,
            'asinh' : mt.asinh, 'acosh' : mt.acosh, 'atanh' : mt.tanh,
            'cosech' : mt.csch, 'sech' : mt.sech, 'coth' : mt.coth}

logInd_dict = {'log' : mt.log, 'exp' : mt.exp, 'log10' : mt.log10}

eqn_parser = {}
eqn_parser.update(trig_dict)
eqn_parser.update(hyp_dict)
eqn_parser.update(logInd_dict)
                  

def checkandParse(string):
  opts2perform = {}
  for key in eqn_parser:
     regex_str = '({})\(([xy\+\-\/\*\.\d]+)\)'.format(key)
     res = re.findall(regex_str, string)
     if len(res) > 0:
       opts2perform[key] = res[0]
  return opts2perform

class TelePlot:
   def __init__(self, x, y, plot_type='scatter', style='default'):
      self.plotType = plot_type
      self.plotStyle = style
      self.xlabel = 'x'
      self.ylabel = 'y'
      self.x = x
      self.y = y
 
   def parseOpts(self, in_array): 
      for opts_tuple in in_array: 
          if 'xaxis' in opts_tuple[0]: 
            print("Got Axis title for x of " + opts_tuple[1])
            self.xlabel = opts_tuple[1] 
          if 'yaxis' in opts_tuple[0]: 
            self.ylabel = opts_tuple[1] 
      plt.xlabel(self.xlabel)
      plt.ylabel(self.ylabel)
      plt.plot(self.x,self.y)
      filename = './{}.png'.format(str(uuid4())[:6])
      plt.savefig(filename)
      return filename
