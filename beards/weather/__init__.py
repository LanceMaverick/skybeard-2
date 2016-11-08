from telegram.ext import CommandHandler
from skybeard.beards import Beard
from . import config, weather

class Weather(Beard):
    
    def initialise(self):
        self.disp.add_handler(CommandHandler('weather', self.forecast))
    
    def forecast(self, bot, update): 
        location = update.message.text.split('/weather',1)[1]
        if not location:
            location = config.default_location
        weather.forecast(update, location)    
