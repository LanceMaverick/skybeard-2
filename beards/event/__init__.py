import os
import logging
import telepot
import telepot.aio
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardAsyncChatHandlerMixin, Filters, regex_predicate, command_predicate
from .event import Event
from .config import Config

config = Config()
curr_path = os.path.dirname(__file__)
#info_path = os.path.join(curr_path, 'yamls/activity.yaml')

class EventManager(telepot.aio.helper.ChatHandler, BeardAsyncChatHandlerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #register all event based commands 
        self.register_command(config.list_evt_kwd, self.event_infos)
        self.register_command(config.new_evt_kwd, self.new_event)

        #commands to modify event values. Handled by single function self.run_cmd()
        event_commands =  [
                config.del_evt_kwd,
                config.res_kwd,
                config.unres_kwd,
                config.rdy_kwd,
                config.unrdy_kwd,
                ]
        #register these commands
        for c in event_commands:
            self.register_command(c, self.run_cmd)
        self.load_events()

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
                    self.events.append(Event(**event_conf))

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
    
    def get_cmd_arg(self, msg):
        """parses message text from a user message that contains an
        event command"""
        try:
            cmd, arg = msg['text'].split(' ', 1)
        except ValueError:
            cmd = msg['text']
            return cmd, None
        else:
            return cmd, arg
    
    async def send_keyboard(self, msg, cmd, events, txt = ''):
        """Sends an inline keyboard to the user or chat

        cmd: The command that triggered the CommandHandler, e.g /event
        events: List of events that the command affects
        txt: Text message to display with the keyboard"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard = [[InlineKeyboardButton(
                text = event.evt_name, 
                callback_data = str(dict(
                    cmd = cmd, 
                    arg = event.init_kwd,
                    chat_id = msg['chat']['id'])))] 
                for event in events])
        await self.sender.sendMessage(txt, reply_markup = keyboard)
    

    async def on_callback_query(self, msg):
        print('here')
        """Callback function for inline keyboard"""
        #get data on what button was pressed
        query_id, from_id, query_data = glance(msg, flavor='callback_query')
        data = eval(query_data)
        cmd = data['cmd']
        arg = data['arg']

        #find out who pressed it and add info to callback_data
        user = dict(
                first_name = msg['from']['first_name'],
                id = from_id)
        data.update(user)
        
        #Find out what type of command.
        #Event creation and modification use separate methods.
        #Keyboard calls back to only one query handler.
        if cmd == ('/'+config.new_evt_kwd):
            await self.new_event(msg, callback_data = data)
        else:
            await self.run_cmd(msg, callback_data = data)
        if data['cmd']!='/event':
            for event in self.events:
                if arg == event.init_kwd:
                    await event.post_details(msg, data, post = dict(
                        chat_id = chat_id,
                        message_id = query_id
                        ))


    async def new_event(self, msg, callback_data = None):
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
            cmd, arg = self.get_cmd_arg(msg)
            user = msg['from']
            par = dict(cmd = cmd, 
                    arg = arg, 
                    first_name = user['first_name'], 
                    id = user['id'], 
                    chat_id = msg['chat']['id'])
        #if event creation called with no argument, send user the keyboard
        if not arg:
            await self.send_keyboard(
                    msg, 
                    cmd,
                    self.events, 
                    txt = 'Please choose one from the list.' 
                    )
            return
        #check if text specifies a time (/event <name> at <time>
        elif ' at ' in arg:
            arg, time = arg.split(' at ', 1)
            par['time'] = time
        
        for event in self.events:
            if event.init_kwd == arg:
                event.new_event(self.bot, msg, par) 
                event.save()
                return
        else:
            await self.send_keyboard(
                    msg, 
                    cmd,
                    self.events, 
                    txt = 'Please choose one from the list.' 
                    )

    async def run_cmd(self, msg, callback_data = None):
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
            cmd, arg = self.get_cmd_arg(msg)
            user = msg['from']
            par = dict(cmd = cmd, 
                    arg = arg, 
                    first_name = user['first_name'], 
                    id = user['id'], 
                    chat_id = msg['chat']['id'])
        
        #if only one event, argument not needed...
        if len(active_events) == 1 and not arg:
            getattr(active_events[0], command_map[cmd.replace('/', '')])(self.bot, msg, par)
            active_events[0].save()
        elif not arg and active_events:
            await self.send_keyboard(
                    msg,
                    cmd,
                    active_events,
                    txt = 'There are several events planned. Please choose one from the list.'
                    )
        #...otherwise ask the user to specify which event
        elif active_events and arg:
            for event in active_events:
                if event.init_kwd == arg:
                    #call relevant method of event
                    getattr(event, command_map[cmd.replace('/', '')])(self.bot, msg, par) 
                    event.save()
                    break
            else:
                await self.send_keyboard(
                        msg, 
                        cmd,
                        active_events, 
                        txt = 'I did not recognise the event name. Please choose one from the list.' 
                        )

    async def event_infos(self, msg):
        """Sends the details of all active events to the user/chat"""
        active_events = self.check_status()
        if not active_events:
            update.message.reply_text('No events planned for today.', quote = False)
        else:
            cmd, arg = self.get_cmd_arg(msg)
            user = msg['from']
            par = dict(cmd = cmd, 
                    arg = arg, 
                    first_name = user['first_name'],
                    id = user['id'], 
                    chat_id = msg['chat']['id'])
            for event in active_events:
                event.post_details(bot, msg, par)
