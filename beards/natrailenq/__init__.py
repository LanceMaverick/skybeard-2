#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler, regex_predicate
from skybeard.decorators import onerror
from . import NatRail
import re

class NationalRailDepartures(BeardChatHandler):
    __userhelp__ = """
    The following commands are available:
     """

    __commands__ = [
        ("departures", "checkTimes", "Displays departures from stated station.\n optional argument ' to [destination]' can be added to refine search."),
        ("journey", "planTrip", "Displays departures from stated station.\n optional argument ' to [destination]' can be added to refine search."),
    ]

    async def planTrip(self, msg):
        natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/', 'beards/natrailenq/station_codes.json')
        out = msg['text'].replace('/journey ','')
        org, dest = re.findall(r'([\w\s\'\(\)\,\&\.]+)(?:to|To|TO)([\w\s\'\(\)\,\&\.]+)\s', out)[0]
        date, time = re.findall(r'(\d\d\/\d\d\/\d\d\d\d|today|Today|now|Now)\s+(\d\d\:\d\d|now|Now)', out)[0]

        natRail.planJourney(org, dest, date, time) 

    @onerror
    async def checkTimes(self, msg):
        natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/', 'beards/natrailenq/station_codes.json')
        out = msg['text'].replace('/departures ','')
        res1 = re.findall(r'(.+)\s(?:To|TO|to)\s(.+)', out)
        if len(res1) == 0:
          res1 = re.findall(r'(.+)', out)
          From  = res1[0] 
          To = ''
        else:
          From, To = res1[0]
        print(res1[0])
        out = natRail.makeDeptString(From,To)
        await self.sender.sendMessage(out, parse_mode="Markdown")
