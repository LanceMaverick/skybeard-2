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
        ("searchstations", "searchStats", "Search stations for key phrase."),
        ("status", "getStatus", "Check status of Train Operating Companies."),
        ("disruptions", "getDisruptions", "Check Information on disruptions to today's services."),
    ]

    @onerror
    async def searchStats(self, msg):
       natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/', 'beards/natrailenq/station_codes.json')
       out = msg['text'].replace('/searchstations ','')
       out, other  = natRail.searchStations(out)
       await self.sender.sendMessage(out)

    async def getStatus(self, msg):
       natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/', 'beards/natrailenq/station_codes.json')
       output = natRail.getStatus()
       await self.sender.sendMessage(output, parse_mode="Markdown")

    async def getDisruptions(self, msg):
       natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/', 'beards/natrailenq/station_codes.json')
       output = natRail.getNews(msg['text'].replace('/disruptions ','').replace('/disruptions',''))
       await self.sender.sendMessage(output, parse_mode="Markdown")

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
        out = natRail.makeDeptString(From,To)
        print(out)
        await self.sender.sendMessage(out, parse_mode="Markdown")
