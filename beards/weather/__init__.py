from skybeard.beards import Beard
from telegram.ext import CommandHandler
from . import forecast

class Weather(Beard):
    
    def initialise(self):
        self.disp.add_handler(CommandHandler('weather', self.forecast))
    
    def forecast(self, bot, update):
        forecast.forecast(bot, update)
