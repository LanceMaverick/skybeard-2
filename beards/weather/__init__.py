from telegram.ext import CommandHandler
from skybeard.beards import Beard
from . import weather

class Weather(Beard):
    
    def initialise(self):
        self.disp.add_handler(CommandHandler('weather', weather.forecast))
    
