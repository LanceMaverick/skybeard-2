import  os
import datetime
from dateutil import parser
import yaml
import config

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
        self.ready = []
        self.create_date = None
        self.begin_time = None
        self.is_evt = False
    
    def clear(self, bot, update, silent = False):
        """ 
        Clears the event attributes and sets it to in-active
        (self.is_evt = False) essentially 'deleting' the event. 
        """
        self.people = []
        self.ready = []
        self.begin_time = None
        self.create_date = None
        self.is_evt = False
#        self.save_status(0)
        if not silent:
            update.message.reply_text(
                    '{} event deleted'.format(self.evt_name), 
                    quote = False)


    def set_time(self, bot, update):
        #TODO: Have time parsed by EventManager
        """
        Sets the start time of the event. Time is interpreted
        from the contents of update.message.text, but in future
        this will be parsed by EventManager
        """
        message = update.message
        text = message.text
        
        try:
            time_from_msg = text.split(' at ', 1)[1]
        except IndexError:
            message.reply_text('Using default time.', quote = False)
            self.begin_time = self.default_time 
        else:
            try:
                parsed_time = parser.parse(time_from_msg)
            except ValueError:
#                message.reply_text('Time could not be pared. Using default')
                self.begin_time = self.default_time
            else:
                if parsed_time.date() == datetime.datetime.today().date():
                    self.begin_time = parsed_time
                else:
                    message.reply_text('Time format not recognised.', quote = False)
                    raise ValueError('event time format not recogised')
        
    def new_event(self, bot, update):
        """
        updates event with a new start time and sets to active.
        does not clear participant information.
        """
        message = update.message
        self.chat_id = message.chat_id
        self.set_time(bot, update)
        self.create_date = datetime.datetime.now()
        self.is_evt = True
        self.participate(bot, update)
        self.post_details(bot, update, header = 'New event:\n')
#        self.save_status(1)
    
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

    def post_details(self, bot, update, header = ''):
        """
        Sends the details of the event to the chat at update.message.chat_id.
        """
        message = update.message
        if not self.is_evt:
            return self.no_event(bot, update)
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
        
        people_str = ', '.join([u[0].first_name for u in self.people])
        if not people_str:
            people_str = 'No-one'
        rdy_str = ', '.join([u[0].first_name for u in self.ready])
        if not rdy_str:
            rdy_str = 'No-one'

        if len(self.people) < self.max_people:
            stack_str = 'No. ({} spaces remaining)'.format(
                    self.max_people - len(self.people))
        elif len(self.people == self.max_people):
            stack_str = 'Yes.'
        else:
            stack_str = 'OVERSTACKED!'

        
        msg = '{}\n{}\n*Participants:* {}\n*Ready:* {}\n*Stacked:* {} '.format(
                info_str, 
                when_str, 
                people_str, 
                rdy_str, 
                stack_str)
        

        message.reply_text(msg, parse_mode='Markdown', quote = False)

    def participate(self, bot, update):
        """ Adds a participant to the event """
        if not self.is_evt:
            return self.no_event(bot, update)
        user = update.message.from_user
        ids = [u[0].id for u in self.people]
        if user.id in ids:
            update.message.reply_text(
                    'You are already participating, {}.'.format(
                user.first_name), quote = False)
        else:
            self.people.append([user, 0])
            update.message.reply_text(
                    '{}, you are now participating.'.format(
                user.first_name), quote = False)

    
    def unparticipate(self, bot, update):
        """ Removes a participant from the event """
        if not self.is_evt:
            return self.no_event(bot, update)
        user = update.message.from_user
        ids = [u[0].id for u in self.people]
        if user.id not in ids:
            update.message.reply_text(
                    'You  are already not participating, {}.'.format(
                user.first_name), quote = False)
        else:
            self.people.append([user, 0])
            update.message.reply_text(
                    '{}, you have been removed.'.format(user.first_name), quote = False)

    def ready_up(self, bot, update):
        """
        Sets a user to 'ready'. Adds them to the participators
        if they are not already.
        """
        if not self.is_evt:
            return self.no_event(bot, update)
        user = update.message.from_user
        ids = [u[0].id for u in self.people]
        if user.id not in ids:
            self.people.append([user, 1])
            update.message.reply_text('You have readied up, {}.'.format(
                user.first_name), quote = False)
        else:
            index = ids.index(user.id)
            status = self.people[index][1]
            if status == 1:
               update.message.reply_text(
                       'You  have already readied up, {}.'.format(
                   user.first_name), quote = False)
            else:
                self.people[index][1]=1
                update.message.reply_text(
                        '{}, you have readied up.'.format(user.first_name), quote = False)
        
    def unready_up(self, bot, update):
        """
        Sets user as not ready to participate
        """
        if not self.is_evt:
            return self.no_event(bot, update)
        user = update.message.from_user
        ids = [u[0].id for u in self.people]
        if user.id not in ids:
            update.message.reply_text(
                    '{}, You are not even participating.'.format(
                user.first_name), quote = False)
        else:
            index = ids.index(user.id)
            status = self.people[index][1]
            if status == 0:
               update.message.reply_text(
                       'You  are already not readied up, {}.'.format(
                   user.first_name), quote = False)
            else:
                self.people[index][1]=0
                update.message.reply_text(
                        '{}, you have cancelled readied up.'.format(user.first_name), quote = False)
        
    def no_event(self, bot, update):
        """ returns message to chat that no event is planned. """
        update.message.reply_text(
                'No {} event scheduled.'.format(self.evt_name), quote = False)

