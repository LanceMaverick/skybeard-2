import logging
from urllib.request import urlopen
import re
import yaml
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler, BeardDBTable
from skybeard.utils import get_args
from .wows import get_player_stats, get_player_ship_stats, find_ship 

logger = logging.getLogger(__name__)

class BoteBeard(BeardChatHandler):
    __commands__ = [
           ('wowsnew',  'add_profile', 'add your profile to the db'),
           ('wowsstats', 'player_stats', 'see your total stats'),
           ('wowsship','ship_stats', 'see your total stats for a particular ship')
           ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("Creating BeardDBTable.")
        self.profile_table = BeardDBTable(self, 'wows_profiles')

    async def add_profile(self, msg):
        await self.sender.sendMessage(
        (
            'Please send me the link to your wargaming open ID.'
            'You can find this on your profile page.'
            ))
        
        reply = await self.listener.wait()
        
        if not 'text' in reply:
            await self.sender.sendMessage('I wasn\'t expecting that. Please try again')
            return
        
        text = reply['text']
        
        if not 'wargaming' in text:
            await self.sender.sendMessage('That doesn\'t seem to be correct. Please try again')
            return
        
        captain_id = re.search(r'.wargaming.net/id/(.*?)-', text).group(1)
        uid = msg['from']['id']
        try:
            int(captain_id)
        except ValueError:
            await self.sender.sendMessage('I dont\t recognise the ID in the link. Please try again')

        new_entry = dict(captain_id = captain_id, uid = uid)

        with self.profile_table as table:
            dupe_check = table.find_one(uid = uid)
            if dupe_check:
                table.update(new_entry, ['uid'])
            else:
                table.insert(new_entry)
            await self.sender.sendMessage('New entry added!')

    async def player_stats(self, msg):
        with self.profile_table as table:
            match = table.find_one(uid = msg['from']['id'])
        if not match:
            await self.sender.sendMessage(
                    (
                        'I do not have your wargaming ID on file.'
                        'Add it with the command /wowsnew.'
                        ))
        details = get_player_stats(match['captain_id'])

        template = '\n'.join([
            '*Your all  time stats:*',
            'name: *{name}*',
            'last played: *{last_played}*',
            'number of battles: *{battles}*',
            'win rate: *{winrate}*',
            'average xp: *{xp}*',
            'max damage record: *{dmg} ({dmg_ship})*',
            'max kills record: *{kill} ({kill_ship})*',
            ])
        try:
            await self.sender.sendMessage(
                    template.format(**details),
                    parse_mode = 'markdown')
        except Exception as e:
            logger.error(e)
            await self.sender.sendMessage(template.format(**details))


    async def ship_stats(self, msg):
        query = ' '.join(get_args(msg))
        if not query:
            await self.sender.sendMessage('Please specify a ship')
            return
    
        ship = find_ship(query)
        if not ship:
            await self.sender.sendMessage(
                    'I could not find a ship that matches "{}"'.format(
                        query))
            return

        with self.profile_table as table:
            match = table.find_one(uid = msg['from']['id'])
        details = get_player_ship_stats(match['captain_id'], ship['id'])
        
        template = '\n'.join([
            'Your all time stats for the *{name}:*',
            'No. of battles: *{battles}*',
            'average damage: *{av_damage}*',
            'average no. of kills: *{kills}*',
            'average xp: *{xp}*',
            'win rate: *{winrate}*',])

        await self.sender.sendPhoto(
            ("ship_photo.jpg",
             urlopen(details['image'])))
        
        await self.sender.sendMessage(
                template.format(**details['stats']), 
                parse_mode = 'markdown')
