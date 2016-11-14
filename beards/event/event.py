import  os
import datetime
from dateutil import parser
import yaml
from telegram.ext import Job
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup
from .config import Config
from .user import UserInfo
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
    def __init__(self, *args, **kwargs):
        """kwargs:
                job_queue:      required for job timing and pushing
                                messaged to the chat/user.

                event_name:     Name used by the bot in messages     

                init_kwd:       Argument used in the chat to call 
                                the event

                max_people:     Maximum number of participants

                warn_time:      How far in advance to reminder 
                                users (minutes).
       """

        
        self.job_queue = kwargs['job_queue']
        self.warn_job = None
        self.delete_job = None
        #event attributes 
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
        
    def get_par(self, update, user_info):
        if user_info:
            return user_info
        else:
            chat_id = update.message.chat_id
            user = update.message.from_user
            return UserInfo(
                    name = user.name,
                    uid = user.id,
                    text = update.message.text,
                    chat_id = chat_id
                    )

    #placeholder functions
    def save(self):
        pass
    def load(self):
        pass

    def clear(self, bot, par, silent = False):
        """ 
        Clears the event attributes and sets it to in-active
        (self.is_evt = False) essentially 'deleting' the event. 
        """
        self.people = []
        self.begin_time = None
        self.create_date = None
        self.is_evt = False
#        self.save_status(0)
        if not silent:
            bot.sendMessage(
                    text = '{} event deleted'.format(self.evt_name), 
                    chat_id = par['chat_id'])

    def set_time(self, bot, par):
        """
        Sets the start time of the event. Time is interpreted
        from the contents of update.message.text, but in future
        this will be parsed by EventManager
        """
        #jobs must be scheduled for removal
        #removed at the end of the interval
        #-> interval set to 1 second to reset
        if self.warn_job:
            self.warn_job.interval = 1
            self.warn_job.schedule_removal()
        if self.delete_job:
            self.delete_job.interval = 1
            self.delete_job.schedule_removal()

        #TODO: Have time parsed by EventManager
        try:
            time = par['time']
        except KeyError:
            bot.sendMessage(
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
                    bot.sendMessage(
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
        self.warn_job = Job(
                self.callback_reminder, 
                time_to_reminder, 
                repeat = False,
                context = par['chat_id'])
        self.job_queue.put(self.warn_job, time_to_reminder)
        
        begin_time = self.begin_time
        #clear time is expiry time (6 hours) + start time - current time
        delete_time = begin_time + datetime.timedelta(hours=6)
        time_to_delete = (delete_time-datetime.datetime.now()).total_seconds()
        self.delete_job = Job(
                self.callback_clear,
                time_to_delete,
                repeat=False,
                context = par['chat_id'])
        self.job_queue.put(self.delete_job, time_to_delete)
       
    def callback_reminder(self, bot, job):
        """
        When the specified warn_time has been reached, the reminder job
        calls back to this
        """
        people = self.people
        unready_users = [u[0] for u in people if u[1] == 0]
        ready_users = [u[0] for u in people if u[1] == 0]

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
        bot.sendMessage(
                text = '*{} will begin in {} minutes!*\n{}'.format(
            self.evt_name, 
            self.warn_time,
            msg_str),
                chat_id=job.context,
                parse_mode = 'Markdown')
    
    def callback_clear(self, bot, job):
        """Clear event attributes"""
        self.people = []
        self.ready = []
        self.begin_time = None
        self.create_date = None
        self.is_evt = False
        
    def new_event(self, bot, par):
        """
        updates event with a new start time and sets to active.
        does not clear participant information.
        """
        self.chat_id = par['chat_id']
        self.set_time(bot, par)
        self.create_date = datetime.datetime.now()
        self.is_evt = True
        self.participate(bot, par)
        self.post_details(bot, par, header = 'New event:\n')
    
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

    def post_details(self, bot, par, header = '', post = None):
        """
        Sends the details of the event to the chat at update.message.chat_id
        If post == True, message will be posted by the event. If False, the
        event will return only the message.
        """
        if not self.is_evt:
            return self.no_event(bot, par)
       
        callback = dict(
                    #info_msg = 1,
                    arg = self.init_kwd,
                    chat_id = par['chat_id'])

        shotgun = config.res_kwd
        unshotgun = config.unres_kwd
        ready = config.rdy_kwd
        unready = config.unrdy_kwd
        print(str(dict(callback, **dict(cmd = '/'+shotgun))))

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton('Shotgun',
                callback_data = str(dict(callback, **dict(cmd = '/'+shotgun)))),
            InlineKeyboardButton('Ready-Up',
                callback_data = str(dict(callback, **dict(cmd = '/'+ready)))),
                ],
                [
            InlineKeyboardButton('Un-shotgun',
                callback_data = str(dict(callback, **dict(cmd = '/'+unshotgun)))),
            InlineKeyboardButton('Not ready',
                callback_data = str(dict(callback, **dict(cmd = '/'+unready)))),
                ]])
        
        msg = self.info_message(header)
        if not post: 
            bot.sendMessage(text = msg,
                    parse_mode='Markdown',
                    reply_markup = keyboard,
                    chat_id = par['chat_id'])
        else:     
            print('=========================', post)
            bot.editMessageText(
                    text=msg,
                    parse_mode='Markdown',
                    reply_markup = keyboard,
                    chat_id = post['chat_id'],
                    message_id = post['message_id'])

    def participate(self, bot, par):
        """ Adds a participant to the event """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if not ids:
            self.people.append([user, 0])
            bot.sendMessage(
                    text = '{}, you are now participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])

        elif user['id'] in ids:
            bot.sendMessage(
                    text = ' {}, you are already participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
        else:
            self.people.append([user, 0])
            bot.sendMessage(
                    text = '{}, you are now participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
    
    def unparticipate(self, bot, par):
        """ Removes a participant from the event """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if user['id'] not in ids or not ids:
            bot.sendMessage(
                    text = '{} you are already not participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
        else:
            index = ids.index(user['id'])
            self.people.pop(index)
            bot.sendMessage(
                    text= '{}, you have been removed from {} .'.format(
                        user['first_name'],
                        self.evt_name), 
                    chat_id = par['chat_id'])

    def ready_up(self, bot, par):
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
            bot.sendMessage(
                    text = '{}, you have readied up for {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
        else:
            index = ids.index(user['id'])
            status = self.people[index][1]
            if status == 1:
               bot.sendMessage(
                       text = '{}, you  have already readied up for {}.'.format(
                   user['first_name'],
                   self.evt_name), 
                       chat_id = par['chat_id'])
            else:
                self.people[index][1]=1
                print(self.people)
                bot.sendMessage(
                        text = '{}, you have readied up for {}.'.format(
                            user['first_name'],
                            self.evt_name), 
                        chat_id = par['chat_id'])
        
    def unready_up(self, bot, par):
        """
        Sets user as not ready to participate
        """
        if not self.is_evt:
            return self.no_event(bot, par)
        user = par
        ids = [u[0]['id'] for u in self.people]
        if user['id'] not in ids or not ids:
            bot.sendMessage(
                    text = '{}, you are not even participating in {}.'.format(
                user['first_name'],
                self.evt_name), 
                    chat_id = par['chat_id'])
            return
        if ids:
            index = ids.index(user['id'])
            status = self.people[index][1]
            if status == 0:
               bot.sendMessage(
                       text = '{} you  are already not readied up for {}.'.format(
                   user['first_name'],
                   self.evt_name), 
                       chat_id = par['chat_id'])
            else:
                self.people[index][1]=0
                bot.sendMessage(
                        text='{}, you have cancelled your ready up for {}.'.format(
                            user['first_name'],
                            self.evt_name), 
                        chat_id = par['chat_id'])
        
    def no_event(self, bot, par):
        """ returns message to chat that no event is planned. """
        bot.sendMessage(
                text = 'No {} event scheduled.'.format(
                    self.evt_name), 
                chat_id = par['chat_id'])

