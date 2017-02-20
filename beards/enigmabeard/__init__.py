import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from skybeard.decorators import onerror
from skybeard.utils import get_args
import enigma
class EnigmaBeard(BeardChatHandler):
    __userhelp__ = """
   	To use the early beta version of the Skybeard Enigma M3 Plugin
        simply use the command <code>encrypt</code> followed by your
        chosen 3 letter key then your message without spaces:
        
        <code>/encrypt NUT THISISAMESSAGE</code> 
     """

    __commands__ = [
        ("encrypt", "encode", "Encode message using M3 Enigma Machine." ),
    ]

    @onerror
    async def encode(self, msg):
        in_args = get_args(msg['text'])
        enigma_m3 = enigma.Enigma('DEBUG')
        enigma_m3.set_key(in_args[0])
        await self.sender.sendMessage(enigma_m3.type_phrase(in_args[1])) 

