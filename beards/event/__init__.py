from skybeard.beards import Beard
import os
import logging
from telegram.ext import CommandHandler, MessageHandler, RegexHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardHide, InlineKeyboardButton
from .config import Config
from .event import Event
config = Config()
curr_path = os.path.dirname(__file__)

class EventManager(Beard):
    """
    A class which instantiates Event objects for any configuration in ./config.py
    and yaml saved configs in ./yamls.
    This class interfaces with the bot's dispatcher and registers commands
    that are universal for every event. The specific events are called with the 
    <init_kwd> argument as set in the individual event configurations. When the 
    call is ambiguous (such as multiple active events, but the user does not 
    specify an argument to the event based command) the Eventmanager will prompt 
    the user to specify using callback buttons.
    """

    def initialise(self):
        self.disp.add_handler(CommandHandler(config.list_evt_kwd, self.event_infos))
        
        self.disp.add_handler(CommandHandler(config.new_evt_kwd, self.new_event))
        self.disp.add_handler(CommandHandler(config.del_evt_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.res_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.unres_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.rdy_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.unrdy_kwd, self.run_cmd))
        self.load_events()

    def load_events(self):
        #load default events configs
        if config.events:
            event_configs = config.events

        #load any user created event configs
        user_event_configs = []
        for fname in os.listdir(os.path.join(curr_path, 'yamls/')):
            if fname.endswith('.yaml'):
                user_event_configs.append(yaml.load(open(fname, 'rb')))

       #instantiate events
        self.events = []         
        if event_configs:
            for event_conf in event_configs:
                try:
                    self.events.append(Event(**event_conf))
                except KeyError as e:
                    logging.error('Wrongly configured event in event config.py: ', e)
        if user_event_configs:     
            for event_conf in user_event_configs:
                try:
                    self.event.append(Event(**event_conf))
                except KeyError as e:
                    logging.error('Wrongly configured user event: ', e)

    def check_status(self):
        active = [event for event in self.events if event.is_evt == True]
        return active
            
    def get_cmd_arg(self, update):
        try:
            cmd, arg = update.message.text.split(' ', 1)
        except ValueError:
            cmd = update.message.text
            return cmd, None
        else:
            return cmd, arg
    
    def send_keyboard(self, bot, update, cmd, events, msg = ''):
        choices = ['{} {}'.format(cmd, event.init_kwd) for event in events]
        markup = ReplyKeyboardMarkup([choices], one_time_keyboard=True)
        update.message.reply_text(msg, reply_markup = markup, quote = False)
#        back = [[InlineKeyboardButton(text=("test"),
#                                      switch_inline_query='')]]
#        bot.answerCallbackQuery(update.callback_query.id,
#                                text=_("test"),
#                                show_alert=False,
#                                timeout=TIMEOUT)
#        
    def hide_keyboard(self, bot, update):
        #markup = ReplyKeyboardHide()
        #update.message.reply_text(reply_markup = markup, text='')
        pass
    
    def new_event(self, bot, update):
        self.hide_keyboard(bot, update)
        cmd, arg = self.get_cmd_arg(update)
        if not arg:
            self.send_keyboard(
                    bot,
                    update, 
                    cmd,
                    self.events, 
                    msg = 'I did not recognise the event name. Please choose one from the list.' 
                    )
            return

        elif ' at ' in arg:
            arg = arg.split(' at ', 1)[0] 
        
        for event in self.events:
            if event.init_kwd == arg:
                event.new_event(bot, update) 
                return
        else:
            self.send_keyboard(
                    bot,
                    update, 
                    cmd,
                    self.events, 
                    msg = 'I did not recognise the event name. Please choose one from the list.' 
                    )

    def run_cmd(self, bot, update):
        self.hide_keyboard(bot, update)
        command_map = {
                config.res_kwd: 'participate',
                config.unres_kwd: 'unparticipate',
                config.rdy_kwd: 'ready_up',
                config.unrdy_kwd: 'unready_up',
                config.del_evt_kwd: 'clear'
                }
       
        active_events = self.check_status() 
        cmd, arg = self.get_cmd_arg(update) 
        if len(active_events) == 1 and not arg:
            getattr(active_events[0], command_map[cmd.replace('/', '')])(bot, update)
        elif not arg and active_events:
            self.send_keyboard(
                    bot,
                    update,
                    cmd,
                    active_events,
                    msg = 'There are several events planned. Please choose one from the list.'
                    )
        elif active_events and arg:
            for event in active_events:
                if event.init_kwd == arg:
                    getattr(event, command_map[cmd.replace('/', '')])(bot, update) 
                    break
            else:
                self.send_keyboard(
                        bot,
                        update, 
                        cmd,
                        active_events, 
                        msg = 'I did not recognise the event name. Please choose one from the list.' 
                        )
         
    def event_infos(self, bot, update):
        active_events = self.check_status()
        if not active_events:
            update.message.reply_text('No events planned for today.', quote = False)
        else:
            for event in active_events:
                event.post_details(bot, update)



            

            
                
                 




        
        
        
        
        #   #maps commands to event methods
         #   command_map = {
         #           config.res_kwd: 'participate',
         #           config.unres_kwd: 'unparticipate',
         #           config.rdy_kwd: 'ready_up',
         #           config.unrdy_kwd: 'unready_up'
         #           }
         #  
         #   message = update.message
         #   if config.new_evt_kwd in cmd:


            


        



            
                

