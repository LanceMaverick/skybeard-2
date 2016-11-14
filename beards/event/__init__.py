from skybeard.beards import Beard
import os
import logging
from telegram.ext import CommandHandler, MessageHandler, RegexHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardHide, InlineKeyboardButton, InlineKeyboardMarkup
from .config import Config
from .event import Event
config = Config()
curr_path = os.path.dirname(__file__)
#info_path = os.path.join(curr_path, 'yamls/activity.yaml')

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
        """Registers all commands and handlers etc. Called automatically when plug-in 
        is loaded. Method also calls load_events() to create each possible event 
        listed in config.py. 
        A job queue to handle the timing of events (reminders and clearing) is
        also created and passed to the events. A CallBackQueryHandler which
        calls back to EventManager.query_callback handles the pressing of 
        inline keyboard buttons. (In it's current configuration there is a risk
        of conflicting with other plugins with in-line buttons)"""
        #register all event based commands 
        self.disp.add_handler(CommandHandler(config.list_evt_kwd, self.event_infos))
        self.disp.add_handler(CommandHandler(config.new_evt_kwd, self.new_event))
        self.disp.add_handler(CommandHandler(config.del_evt_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.res_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.unres_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.rdy_kwd, self.run_cmd))
        self.disp.add_handler(CommandHandler(config.unrdy_kwd, self.run_cmd))
        #add callback handler for inline keyboard
        self.disp.add_handler(CallbackQueryHandler(self.query_callback))
        #add job queue for event timing
        self.job_queue = self.updater.job_queue
        
        #instantiate all available event types
        self.load_events()
    
    def save_event(self, event):
        """Dummy method that will save the event status in the future"""
        event.save()
        
    def load_events(self):
        """loads all event configurations"""
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
            for i, event_conf in enumerate(event_configs):
                try:
                    self.events.append(Event(**event_conf, job_queue=self.job_queue))

                except KeyError as e:
                    logging.error('Wrongly configured event in event config.py: ', e)
                else:
                    self.events[i].save()
        if user_event_configs:     
            for event_conf in user_event_configs:
                try:
                    self.event.append(Event(**event_conf))
                except KeyError as e:
                    logging.error('Wrongly configured user event: ', e)

    def check_status(self):
        """Returns a list of the events that are currently active
        (event.is_evt == True)"""
        active = [event for event in self.events if event.is_evt == True]
        return active
            
    def get_cmd_arg(self, update):
        """parses message text from a user message that contains an
        event command"""
        try:
            cmd, arg = update.message.text.split(' ', 1)
        except ValueError:
            cmd = update.message.text
            return cmd, None
        else:
            return cmd, arg
    
    def send_keyboard(self, bot, update, cmd, events, msg = ''):
        """Sends an inline keyboard to the user or chat

        cmd: The command that triggered the CommandHandler, e.g /event
        events: List of events that the command affects
        msg: Text message to display with the keyboard"""
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                event.evt_name, 
                callback_data = str(dict(
                    cmd = cmd, 
                    arg = event.init_kwd,
                    chat_id = update.message.chat_id)))] 
                for event in events])
        update.message.reply_text(text=msg, reply_markup = keyboard, quote = False)
    
    def query_callback(self, bot, update):
        """Callback function for inline keyboard"""
        #get data on what button was pressed
        query = update.callback_query
        data = eval(query.data)
        cmd = data['cmd']
        arg = data['arg']

        #find out who pressed it and add info to callback_data
        user = dict(
                first_name = query.from_user.first_name,
                id = query.from_user.id)
        data.update(user)
        
        #Find out what type of command.
        #Event creation and modification use separate methods.
        #Keyboard calls back to only one query handler.
        if cmd == ('/'+config.new_evt_kwd):
            self.new_event(bot, update, callback_data = data)
        else:
            self.run_cmd(bot, update, callback_data = data)
        if data['cmd']!='/event':
            for event in self.events:
                if arg == event.init_kwd:
                    event.post_details(bot, data, post = dict(
                        chat_id = query.message.chat_id,
                        message_id = query.message.message_id
                        ))


    def new_event(self, bot, update, callback_data = None):
        """create new events (sets attributes in already instantiated
        but deactivated events)
        
        callback_data:  If call_back data exits, it is used to get user
                        and command information. Otherwise the update 
                        object is used. This is so the method can 
                        handle text commands and button callbacks"""

        #check for callback data. 
        if callback_data:
            cmd = callback_data['cmd']
            arg = callback_data['arg']
            par = callback_data
        #default to update object
        else:
            cmd, arg = self.get_cmd_arg(update)
            user = update.message.from_user
            par = dict(cmd = cmd, 
                    arg = arg, 
                    first_name = user.first_name, 
                    id = user.id, 
                    chat_id = update.message.chat_id)
        #if event creation called with no argument, send user the keyboard
        if not arg:
            self.send_keyboard(
                    bot,
                    update, 
                    cmd,
                    self.events, 
                    msg = 'Please choose one from the list.' 
                    )
            return
        #check if text specifies a time (/event <name> at <time>
        elif ' at ' in arg:
            arg, time = arg.split(' at ', 1)
            par['time'] = time
        
        for event in self.events:
            if event.init_kwd == arg:
                event.new_event(bot, par) 
                event.save()
                return
        else:
            self.send_keyboard(
                    bot,
                    update, 
                    cmd,
                    self.events, 
                    msg = 'Please choose one from the list.' 
                    )

    def run_cmd(self, bot, update, callback_data = None):
        """Parsing function for all event modification commands

        callback_data:  If call_back data exits, it is used to get user
                        and command information. Otherwise the update 
                        object is used. This is so the method can 
                        handle text commands and button callbacks"""

        #link commands to methods in Event class
        command_map = {
                config.res_kwd: 'participate',
                config.unres_kwd: 'unparticipate',
                config.rdy_kwd: 'ready_up',
                config.unrdy_kwd: 'unready_up',
                config.del_evt_kwd: 'clear'
                }
        #check for active events
        active_events = self.check_status() 

        #use callback data instead of update, if it exists
        if callback_data:
            cmd = callback_data['cmd']
            arg = callback_data['arg']
            par = callback_data
            
        else:
            cmd, arg = self.get_cmd_arg(update)
            user = update.message.from_user
            par = dict(cmd = cmd, 
                    arg = arg, 
                    first_name = user.first_name, 
                    id = user.id, 
                    chat_id = update.message.chat_id)
        
        #if only one event, argument not needed...
        if len(active_events) == 1 and not arg:
            getattr(active_events[0], command_map[cmd.replace('/', '')])(bot, par)
            active_events[0].save()
        elif not arg and active_events:
            self.send_keyboard(
                    bot,
                    update,
                    cmd,
                    active_events,
                    msg = 'There are several events planned. Please choose one from the list.'
                    )
        #...otherwise ask the user to specify which event
        elif active_events and arg:
            for event in active_events:
                if event.init_kwd == arg:
                    #call relevant method of event
                    getattr(event, command_map[cmd.replace('/', '')])(bot, par) 
                    event.save()
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
        """Sends the details of all active events to the user/chat"""
        active_events = self.check_status()
        if not active_events:
            update.message.reply_text('No events planned for today.', quote = False)
        else:
            cmd, arg = self.get_cmd_arg(update)
            user = update.message.from_user
            par = dict(cmd = cmd, 
                    arg = arg, 
                    first_name = user.first_name, 
                    id = user.id, 
                    chat_id = update.message.chat_id)
            for event in active_events:
                event.post_details(bot, par)
