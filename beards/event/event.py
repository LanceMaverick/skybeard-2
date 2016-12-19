import  os
import datetime
from dateutil import parser
import yaml
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from .config import Config
import logging

config = Config()
curr_path = os.path.dirname(__file__)
info_path = os.path.join(curr_path, 'yamls/activity.yaml')

class Event(object):
    """
    General event class which handles the tracking of an event,
    it's time and participants. The mandatory keyword arguments
    are:
    event_name: The name that the bot uses for the event

    init_kwd:   How the event is called, as an argument to commands
                in the telegram chat, e.g /event <init_kwd>

    max_people: The maximum number of people who can participate

    warn_time:  The EventManager will remind the users shortly
                before the event starts. This sets the amount 
                of time between reminder and event start time in
                minutes.
    """
    def __init__(self, **kwargs):
        #event name, used in the chat
        self.evt_name = kwargs['event_name']
        #name of event for telegram command argumnt, to init a new event
        self.init_kwd = kwargs['init_kwd']

        #time event defaults to if no time is set
        self.def_time = kwargs.get('default_time', dict(hour = 19, minute = 30))
        self.default_time = datetime.datetime.now().replace(**self.def_time)
        #maximum allowed people for the event
        self.max_people = kwargs['max_people']
        #time in minutes before warning message is sent
        self.warn_time = kwargs['warn_time']
        
        
        self.part_name = ['shotgun', 'shotgunned']

        self.people = []
        self.create_date = None
        self.begin_time = None
        self.is_evt = False

        #used by the scheduler to set timers
        self.event_data = kwargs
        
    #placeholder functions
    def save(self):
        pass
    def load(self):
        pass

    async def set_time(self, bot, par):
        """
        Sets the start time of the event. Time is interpreted
        from the contents of update.message.text, but in future
        this will be parsed by EventManager
        """
        #jobs must be scheduled for removal
        #removed at the end of the interval
        #-> interval set to 1 second to reset
        
        #TODO implement scheduler
        #if self.warn_job:
        #    self.warn_job.interval = 1
        #    self.warn_job.schedule_removal()
        #if self.delete_job:
        #    self.delete_job.interval = 1
        #    self.delete_job.schedule_removal()

        
        #TODO: Have time parsed by EventManager
        try:
            time = par['time']
        except KeyError:
            await bot.sendMessage(
                    chat_id = par['chat_id'], 
                    text = 'Using default time.')
            self.begin_time = self.default_time 
        else:
            try:
                parsed_time = parser.parse(time)
            except ValueError:
#                message.reply_text('Time could not be pared. Using default')
                self.begin_time = self.default_time
            else:
                if parsed_time.date() == datetime.datetime.today().date():
                    self.begin_time = parsed_time
                else:
                    await bot.sendMessage(
                            text='Time format not recognised.', 
                            chat_id = par['chat_id'])
                    raise ValueError('event time format not recogised')
        
        #setting up jobs for reminders and clearing of old events
        warn_time_seconds = self.warn_time*60
        dtime = self.calc_dtime()
        dtime_total_seconds = dtime['dtime'].total_seconds()

        #time to reminder is:
        #time between event creation and even start minus reminder time
        #all in seconds
        time_to_reminder = dtime_total_seconds - warn_time_seconds

        
        begin_time = self.begin_time
        #clear time is expiry time (6 hours) + start time - current time
        delete_time = begin_time + datetime.timedelta(hours=6)
        time_to_delete = (delete_time-datetime.datetime.now()).total_seconds()
        
    def callback_reminder(self):
        """
        When the specified warn_time has been reached, the reminder job
        calls back to this
        """
        people = self.people
        unready_users = [u[0]['first_name'] for u in people if u[1] == 0]
        ready_users = [u[0]['first_name'] for u in people if u[1] == 0]

        if not unready_users:
            unready_str = 'No-one'
        else:
            unready_str = ', '.join(unready_users)
        if not ready_users:
            ready_str = 'No-one'
        else:
            ready_str = ', '.join(ready_users)
        
        msg_str = '*Ready:* {}\n*Not ready:* {}\n'.format(
                ready_str, unready_str)
        return '*{} will begin in {} minutes!*\n{}'.format(
                self.evt_name, 
                self.warn_time,
                msg_str)
    
    async def clear(self, *args):
        """Clear event attributes"""
        self.people = []
        self.ready = []
        self.begin_time = None
        self.create_date = None
        self.is_evt = False
        
    async def new_event(self, bot, msg, par):
        """
        updates event with a new start time and sets to active.
        does not clear participant information.
        """
        self.chat_id = par['chat_id']
        await self.set_time(bot, par)
        self.create_date = datetime.datetime.now()
        self.is_evt = True
        await self.participate(bot, par)
        await self.post_details(bot, msg, par, header = 'New event:\n')
    
    def calc_dtime(self):
        """
        Calculates the time difference between the moment the 
        function is called and the start of the event.
        Returns a dictionary of the timedelta object and
        the hours, minutes and seconds.
        """
        now = datetime.datetime.now()
        evt_time = self.begin_time
        dtime =  evt_time - now
        days, seconds = dtime.days, dtime.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return dict(
                dtime=dtime,
                hours=hours,
                minutes=minutes,
                seconds=seconds)

    def info_message(self, header = ''):
        """returns formatted string detailing the event status"""
        info_str = '{}*{} at {}*'.format(
                header,
                self.evt_name,
                self.begin_time.strftime("%H:%M"))
        
        dtime = self.calc_dtime()
        if dtime['hours'] >  0:
            when_str = 'Event begins in {} hours and {} minutes.'.format(
                    str(dtime['hours']), 
                    str(dtime['minutes'])
                    )
        else:
            when_str = 'Event already began.'
        
        people_str = ', '.join([u[0]['first_name'] for u in self.people])
        if not people_str:
            people_str = 'No-one'
        rdy_str = ', '.join([u[0]['first_name'] for u in self.people if u[1]==1])
        if not rdy_str:
            rdy_str = 'No-one'

        if len(self.people) < self.max_people:
            stack_str = 'No. ({} spaces remaining)'.format(
                    self.max_people - len(self.people))
        elif len(self.people) == self.max_people:
            stack_str = 'Yes.'
        else:
            stack_str = 'OVERSTACKED!'
        
        msg = '{}\n{}\n*Participants:* {}\n*Ready:* {}\n*Stacked:* {} '.format(
                info_str, 
                when_str, 
                people_str, 
                rdy_str, 
                stack_str)
        
        return msg

    async def post_details(self, bot, msg, par, header = '', post = None):
        """
        Sends the details of the event to the chat at update.message.chat_id
        If post == True, message will be posted by the event. If False, the
        event will return only the message.
        """

        if not self.is_evt:
            await self.no_event(bot, par)
            return
       
        callback = dict(
                    arg = self.init_kwd,
                    chat_id = par['chat_id'])

        shotgun = config.res_kwd
        unshotgun = config.unres_kwd
        ready = config.rdy_kwd
        unready = config.unrdy_kwd

        keyboard = InlineKeyboardMarkup(
                inline_keyboard = [[
            InlineKeyboardButton(text = 'Shotgun',
                callback_data = str(dict(callback, **dict(cmd = '/'+shotgun)))),
            InlineKeyboardButton(text = 'Ready-Up',
                callback_data = str(dict(callback, **dict(cmd = '/'+ready)))),
                ],
                [
            InlineKeyboardButton(text = 'Un-shotgun',
                callback_data = str(dict(callback, **dict(cmd = '/'+unshotgun)))),
            InlineKeyboardButton(text = 'Not ready',
                callback_data = str(dict(callback, **dict(cmd = '/'+unready)))),
                ]])
        
        txt = self.info_message(header)
        if not post: 
            await bot.sendMessage(text = txt,
                    parse_mode='Markdown',
                    reply_markup = keyboard,
                    chat_id = par['chat_id'])
        else:     
            #strange telegram bug causes thread crash when
            #editing message to be the same (e.g same callback button
            #pressed twice. Message is first edited to be reverse of
            #true message, before editing to be the correct updated
            #message
            await bot.editMessageText(
                    telepot.origin_identifier(msg),
                    text = txt[::-1],
                    parse_mode='Markdown'
                    )
            await bot.editMessageText(
                   telepot.origin_identifier(msg),
                   text = txt,
                   parse_mode='Markdown',
                   reply_markup = keyboard
                   )

    async def participate(self, bot, par):
        """ Adds a participant to the event """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if not ids:
            self.people.append([user, 0])
            await bot.sendMessage(
                    text = '{}, you are now participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])

        elif user['id'] in ids:
            await bot.sendMessage(
                    text = ' {}, you are already participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
        else:
            self.people.append([user, 0])
            await bot.sendMessage(
                    text = '{}, you are now participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
    
    async def unparticipate(self, bot, par):
        """ Removes a participant from the event """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if user['id'] not in ids or not ids:
            await bot.sendMessage(
                    text = '{} you are already not participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
        else:
            index = ids.index(user['id'])
            self.people.pop(index)
            await bot.sendMessage(
                    text= '{}, you have been removed from {} .'.format(
                        user['first_name'],
                        self.evt_name), 
                    chat_id = par['chat_id'])

    async def ready_up(self, bot, par):
        """
        Sets a user to 'ready'. Adds them to the participators
        if they are not already.
        """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if user['id'] not in ids or not ids:
            self.people.append([user, 1])
            await bot.sendMessage(
                    text = '{}, you have readied up for {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
        else:
            index = ids.index(user['id'])
            status = self.people[index][1]
            if status == 1:
               await bot.sendMessage(
                       text = '{}, you  have already readied up for {}.'.format(
                   user['first_name'],
                   self.evt_name), 
                       chat_id = par['chat_id'])
            else:
                self.people[index][1]=1
                await bot.sendMessage(
                        text = '{}, you have readied up for {}.'.format(
                            user['first_name'],
                            self.evt_name), 
                        chat_id = par['chat_id'])
        
    async def unready_up(self, bot, par):
        """
        Sets user as not ready to participate
        """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if user['id'] not in ids or not ids:
            await bot.sendMessage(
                    text = '{}, you are not even participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
            return
        if ids:
            index = ids.index(user['id'])
            status = self.people[index][1]
            if status == 0:
               await bot.sendMessage(
                       text = '{} you  are already not readied up for {}.'.format(
                   user['first_name'],
                   self.evt_name), 
                       chat_id = par['chat_id'])
            else:
                self.people[index][1]=0
                await bot.sendMessage(
                        text='{}, you have cancelled your ready up for {}.'.format(
                            user['first_name'],
                            self.evt_name), 
                        chat_id = par['chat_id'])
        
    async def no_event(self, bot, par):
        """ returns message to chat that no event is planned. """
        await bot.sendMessage(
                text = 'No {} event scheduled.'.format(
                    self.evt_name), 
                chat_id = par['chat_id'])

