import  os
import datetime
from dateutil import parser
from telegram.ext import CommandHandler, MessageHandler, RegexHandler, Filters
import yaml

curr_path = os.path.dirname(__file__)
info_path = os.path.join(curr_path, 'yamls/activity.yaml')

"""Mixin class for general event creation/management functionality.
evt_name, max_people, init_cmd, res_kwd, unres_kwd, rdy_kwd, unrdy_kwd,
warn_time and info_cmd
are typically set in the plug-in interface of __init.py__
"""

class EventMixin(object):
    #event attributes 
    #event name, used in the chat
    evt_name = 'event'
    #maximum allowed people for the event
    max_people = None
    #command (called in tg with /) to init a new event
    init_cmd = 'event'
    #keywords to reserve a place
    res_kwd = 'shotgun!'
    #keyworkds to unreserve a place
    unres_kwd = 'unshotgun!'
    #keywords to decare readiness
    rdy_kwd = 'rdry!'
    #keywords to undeclare readiness
    unrdy_kwd = 'unrdry!'
    warn_time = 5
    info_cmd = 'eventinfo'

    #aesthetic stuff
    part_name = ['shotgun', 'shotgunned']
    default_time = datetime.datetime.now().replace(
            hour=19, minute = 30)

    #telegrm specific 
    
    def initialise(self):
        print('initialiasing')
        self.disp.add_handler(CommandHandler(self.init_cmd, self.new_event))
        self.disp.add_handler(CommandHandler('delete', self.clear))
        re_exp = '^\s*A*\s*$'
        # '(?:^|\W)rocket(?:$|\W)'
        part_re = re_exp.format(self.res_kwd)
        unpart_re = re_exp.format(self.unres_kwd)
        rdy_re = re_exp.format(self.rdy_kwd)
        unrdy_re = re_exp.format(self.unrdy_kwd)

        self.disp.add_handler(RegexHandler(part_re, self.participate))
        self.disp.add_handler(RegexHandler(unpart_re, self.unparticipate))
        self.disp.add_handler(RegexHandler(rdy_re, self.ready_up))
        self.disp.add_handler(RegexHandler(unrdy_re, self.unready_up))
        
#        self.remind_job = Job(self.check_remind, 86400.0) #24 hours in seconds
#        self.clear_job = Job(learn.check_clear, ) #24 hours in seconds 

    def __init__(self, *args, **kwargs):
        self.people = []
        self.ready = []
        self.create_date = None
        self.begin_time = None
        self.is_evt = False

    def clear(self):
        self.people = []
        self.ready = []
        self.begin_time = None
        self.create_date = None
        self.is_evt = False
#        self.save_status(0)


    def set_time(self, bot, update):
        message = update.message
        text = message.text
        
        try:
            time_from_msg = text.split('at', 1)[1]
        except IndexError:
            message.reply_text('Using detault time.')
            self.begin_time = self.default_time 
        else:
            parsed_time = parser.parse(time_from_msg)
            if parsed_time.date() == datetime.datetime.today().date():
                self.begin_time = parsed_time
            else:
                message.reply_text('Time format not recognised.')
                raise ValueError('event time format not recogised')
        
    """updates event with a ne start time and sets to active.
    does not clear participant information."""
    def new_event(self, bot, update):
     
        message = update.message
        self.chat_id = message.chat_id
        self.creator = message.from_user
        
        self.people.append(self.creator) 
        self.set_time(bot, update)
        self.create_date = datetime.datetime.now()
        self.is_evt = True
        self.post_details(message, header = 'New event:\n')
#        self.save_status(1)

    def calc_dtime(self):
        now = datetime.datetime.now()
        evt_time = self.begin_time
        dtime =  evt_time - now
        days, seconds = dtime.days, dtime.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return dict(dtime=dtime, hours=hours, minutes=minutes, seconds=seconds)

    def post_details(self, message, header = ''):
        if not self.is_evt:
            return self.no_event()
        info_str = '{}*{} event at {}*'.format(header, self.evt_name, self.begin_time.strftime("%H:%M"))
        
        dtime = self.calc_dtime()
        if dtime['hours'] >  0:
            when_str = 'Event begins in {} hours and {} minutes.'.format(
                    str(dtime['hours']), 
                    str(dtime['minutes'])
                    )
        else:
            when_str = 'Event already began.'
        
        people_str = ', '.join([u.first_name for u in self.people])
        if not people_str:
            people_str = 'No-one'
        rdy_str = ', '.join([u.first_name for u in self.ready])
        if not rdy_str:
            rdy_str = 'No-one'
        
        msg = '{}\n{}\n*Participants:* {}\n*Ready:* {} '.format(info_str, when_str, people_str, rdy_str)
        

        message.reply_text(msg, parse_mode='Markdown')

    def participate(self, bot, update):
        if not self.is_evt:
            return self.no_event()
        user = update.message.user
        ids = [u[0].id for u in self.people]
        if user.id in ids:
            update.message.reply_text('You are already participating, {}.'.format(
                user.first_name))
        else:
            self.people.append([user, 0])
            update.message.reply_text('{}, You are now participating.'.format(
                user.first_name))

    
    def unparticipate(self, bot, update):
        if not self.is_evt:
            return self.no_event()
        user = update.message.user
        ids = [u[0].id for u in self.people]
        if user.id not in ids:
            update.message.reply_text('You  are already not participating, {}.'.format(
                user.first_name))
        else:
            self.people.append([user, 0])
            update.message.reply_text('{}, you have been removed.'.format(user.first_name))

    def ready_up(self, bot, update):
        if not self.is_evt:
            return self.no_event()
        user = update.message.user
        ids = [u[0].id for u in self.people]
        if user.id not in ids:
            self.people.append([user, 1])
            update.message.reply_text('You have readied up, {}.'.format(
                user.first_name))
        else:
            index = ids.index(user.id)
            status = self.people(index)[1]
            if status == 1:
               update.message.reply_text('You  have already readied up, {}.'.format(
                   user.first_name))
            else:
                self.people[index][1]=1
                update.message.reply_text('{}, you have readied up.'.format(user.first_name))
        
    def unready_up(self, bot, update):
        if not self.is_evt:
            return self.no_event()
        user = update.message.user
        ids = [u[0].id for u in self.people]
        if user.id not in ids:
            update.message.reply_text('{}, You are not even participating.'.format(
                user.first_name))
        else:
            index = ids.index(user.id)
            status = self.people(index)[1]
            if status == 0:
               update.message.reply_text('You  are already not readied up, {}.'.format(
                   user.first_name))
            else:
                self.people[index][1]=0
                update.message.reply_text('{}, you have cancelled readied up.'.format(user.first_name))
        
    def no_event(self, bot, update):
        update.message.reply_text('No {} event scheduled.'.format(self.evt_name))

