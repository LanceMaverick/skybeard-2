import telepot
import telepot.aio
import digitalocean
from skybeard.beards import BeardChatHandler
from . import config

class DigOcean(BeardChatHandler):

    __userhelp__="""
    If the bot is being hosted on digital ocean,
    this allows user to get network stats if they are
    an admin
    /donet to post the ip of your droplet
    only works for people in the admins list in config,py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command('donet', self.get_ip)

    async def get_ip(self, msg):
        user_id = msg['from']['id']
        if not any(int(d['id']) == user_id for d in config.admins):
            await self.sender.sendMessage('You do not have persmission to use this command')
            return
        else:
            manager = digitalocean.Manager(token=config.api_key)
            droplets = manager.get_all_droplets()
            droplet_info = []
            for droplet in droplets:
                droplet_info.append(
                    [droplet.name, droplet.networks['v4'][0]['ip_address']]
                    )
            message = ['The IP adresses of your droplets are:']
            for info in droplet_info:
                message.append('*{}:* {}'.format(info[0], info[1]))
            await self.sender.sendMessage('\n'.join(message), parse_mode = 'markdown')
                








