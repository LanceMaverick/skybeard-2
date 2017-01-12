#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler, regex_predicate
from . import NatRail

class NationalRailDepartures(BeardChatHandler):
    __userhelp__ = """
    The following commands are available:
     """

    __commands__ = [
        ("departures", "checkTimes", "Calculates route from [origin] to [destination]"),
    ]


    async def checkTimes(self, msg):
        natRail = NatRail.RailScraper('http://ojp.nationalrail.co.uk/service/ldbboard/dep/', 'beards/natrailenq/station_codes.json')
        out = natRail.makeDeptString(msg['text'])
        await self.sender.sendMessage(out)
