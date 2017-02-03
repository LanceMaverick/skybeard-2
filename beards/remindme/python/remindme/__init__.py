import logging
from dateutil import parser
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)

class RemindMe(BeardChatHandler):
    __userhelp__ = """
    A simple reminder that will remind you of an event
    later the same day.
    To use, send the command /remindme"""
    __commands__ = [
            ('remindme', 'start_convo', 'set up a reminder for later today')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router.routing_table['_remind'] = self.on__remind

    async def start_convo(self, msg):
        await self.sender.sendMessage('Please specify a name for the reminder')
        reply = await self.listener.wait()
        event = dict(name_msg = reply)
        data = self.scheduler.make_event_data('_chat', event)
        await self.set_remind_time(data)
    
    async def set_remind_time(self, event):
        await self.sender.sendMessage('When would you like reminding?')
        reply = await self.listener.wait()
        text = reply['text']
        if text.startswith('in'):
            try:
                txt_split = text.split(' ')
                t = int(txt_split[1])
                units = txt_split[2]
            except (ValueError, IndexError) as e:
                logger.debug(e, 'remindme time not recognised')
                await self.sender.sendMessage('Sorry I did not recognise that time')
                return

            if any([units == u for u in ['hours', 'hour', 'hr', 'hrs']]):
                time = t*60*60
            elif any([units == u for u in ['minutes', 'minute', 'min', 'mins']]):
                time = t*60
            elif any([units == u for u in ['seconds', 'second', 'sec', 'secs']]):
                time = t
            else:
                logger.debug('remindme time not recognised: '+text)
                await self.sender.sendMessage('Sorry I did not recognise that time')
            t_string = ' '.join(txt_split[1:])
            self.scheduler.event_later(time, ('_remind', event))
        else:
            try:
                dt = parser.parse(text)
            except ValueError as e:
                logger.debug(e, 'remindme time not recognised')
                await self.sender.sendMessage('Sorry I did not recognise that time')
                return
            time = dt.timestamp()
            t_string = dt.strftime('%b %d %Y %I:%M%p')
            self.scheduler.event_at(time, ('_remind', event))

        await self.sender.sendMessage('Reminder set for:\n'+t_string)
        
    async def on__remind(self, data):
        d = data['_remind']['_chat']['name_msg']
        user = d['from']['first_name']
        text = d['text']

        await self.sender.sendMessage(
                'Reminder for {}:\n"{}"'.format(user, text))

