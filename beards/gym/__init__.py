from telegram.ext import CommandHandler, MessageHandler, Filters
from skybeard.beards import Beard
from . import gym

class Gym(Beard):

    def initialise(self):
        self.disp.add_handler(CommandHandler('newgym', gym.add_gym))
        self.disp.add_handler(MessageHandler(Filters.text, self.gainz_pics))
        self.disp.add_handler(MessageHandler(Filters.location, gym.visit))

    def gainz_pics(self, bot, update):
        if 'gainz' in update.message.text:
            gym.pics(bot, update)
        
