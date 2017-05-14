#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror
from skybeard.utils import get_args
from . import NatRail
from . import config
import re


def format_msg(msg):
    text = msg['text']
    return ' '.join(get_args(text)).title()


class NationalRailDepartures(BeardChatHandler):
    __userhelp__ = """
    The following commands are available:
     """

    __commands__ = [
        ("departures", "checkTimes", "Displays departures from stated station."),
        ("searchstations", "searchStats", "Search stations for key phrase."),
        ("status", "getStatus", "Check status of Train Operating Companies."),
        ("disruptions", "getDisruptions", "Check Information on disruptions to today's services."),
    ]

    @onerror()
    async def searchStats(self, msg):
        natRail = NatRail.RailScraper(config.rail_url, config.stat_codes)
        out = format_msg(msg)
        out, other = natRail.searchStations(out)
        await self.sender.sendMessage(out)

    @onerror()
    async def getStatus(self, msg):
        natRail = NatRail.RailScraper(config.rail_url, config.stat_codes)
        output = natRail.getStatus()
        await self.sender.sendMessage(output, parse_mode="Markdown")

    @onerror()
    async def getDisruptions(self, msg):
        natRail = NatRail.RailScraper(config.rail_url, config.stat_codes)
        output = natRail.getNews(format_msg(msg))
        await self.sender.sendMessage(output, parse_mode="Markdown")

    @onerror()
    async def checkTimes(self, msg):
        natRail = NatRail.RailScraper(config.rail_url, config.stat_codes)
        out = format_msg(msg)
        res1 = re.findall(r'(.+)\s(?:To|TO|to)\s(.+)', out)
        if not res1:
            res1 = re.findall(r'(.+)', out)
            From = res1[0]
            To = ''
        else:
            From, To = res1[0]
        out = natRail.makeDeptString(From, To)
        print(out)
        await self.sender.sendMessage(out, parse_mode="Markdown")
