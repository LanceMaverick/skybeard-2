#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler, regex_predicate
from . import NatRail
import re

class NationalRailDepartures(BeardChatHandler):
    __userhelp__ = """
    The following commands are available:
     """

    __commands__ = [
        ("departures", "checkTimes", "Displays departures from stated station.\n optional argument ' to [destination]' can be added to refine search."),
    ]


    async def checkTimes(self, msg):
        natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/ldbboard/dep/', 'beards/natrailenq/station_codes.json')
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
