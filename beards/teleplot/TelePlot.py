import matplotlib.pyplot as plt
from uuid import uuid4


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
