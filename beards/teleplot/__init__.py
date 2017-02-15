#show spacecats test plugin
# Adapted from work by LanceMaverick
import logging
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from skybeard.decorators import onerror
from skybeard.utils import get_args
from . import TelePlot as tp
import os
import equatic
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
        logger = logging.getLogger("TelePlot")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()
        in_args = get_args(msg['text']) 
        logger.debug("Got arguments: %s", in_args)
        options = []
         
        for element in in_args:
            if element in ['-xlabel', '-ylabel', '-range']:
                logger.debug("Found option '%s'", element)
                arg_index = in_args.index(element)
                logger.debug("Adding option (%s, %s)", element, in_args[arg_index+1])
                options.append((element, in_args[arg_index+1]))

        plotter = tp.TelePlot(in_args[0], options, debug='ERROR')
        try:
            file_name = plotter.save_plot()
            await self.sender.sendPhoto(('temp.png', open('{}'.format(file_name), 'rb')))
            os.remove('{}'.format(file_name))
        except SystemExit:
            logger.error("Invalid User Input")
            await self.sender.sendMessage("Ooops! I did not understand your request.")
