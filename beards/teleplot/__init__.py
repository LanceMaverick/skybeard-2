#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from skybeard.decorators import onerror
from skybeard.utils import get_args
from . import TelePlot
import os

class TelePlotSB(BeardChatHandler):
    __userhelp__ = """
    Makes plots with the /teleplot command. e.g:
    From two arrays: /teleplot [x1,x2,..,xN] [y1,y2,..,yN]
    From an expression: /teleplot (x**2+2*x+3)
    Additional options: -xaxis "label", -yaxis "label"
    Currently only index, add, subtract, divide, multiply 
    available for equation notation."
     """

    __commands__ = [
        ("teleplot", "makePlot", "make a plot." ),
    ]

    @onerror
    async def makePlot(self, msg):
        in_args = get_args(msg['text']) 
     
        options = []
         
        for element in in_args:
            if element in ['-xlabel', '-ylabel', '-range']:
                arg_index = in_args.find(element)
                options.append(element, in_args[arg_index+1])

        plotter = Teleplot.Teleplot(in_args[0], options)
        file_name = plotter.save_plot()
        await self.sender.sendPhoto(('temp.png', open('{}'.format(file_name), 'rb')))
        os.remove('{}'.format(file_name))
