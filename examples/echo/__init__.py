import telepot
import telepot.aio
from skybeard.beards import BeardAsyncChatHandlerMixin

class Echo(BeardChatHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #register command "/hello" to dispatch to self.say_hello()
        self.register_command("hello", self.say_hello)
    
    #is called when "/hello" is sent
    async def say_hello(self, msg):
        name = msg['from']['first_name']
        await self.sender.sendMessage('Hello {}!'.format(name))
    
    #is called every time a message is sent
    async def on_chat_message(self, msg):
        text = msg['text']
        await self.sender.sendMessage(text)
        await super().on_chat_message(msg)
