from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Job
from skybeard.beards import Beard
from .event import EventMixin


class TestEvent(EventMixin, Beard):
    evt_name = 'test event'
    max_people = 5
    init_cmd = 'testevent'

class OverWatchEvent(EventMixin, Beard):
    evt_name = 'Overwatch'
    max_people = 6
    init_cmd = 'overwatch'

class WarshipsEvent(EventMixin, Beard):
    evt_name = 'History Boats'
    max_people = 3
    init_cmd = 'botes'

class FracSpaceEvent(EventMixin, Beard):
    evt_name = 'space Boats'
    max_people = 5
    init_cmd = 'spotes'
    
class DotaEvent(EventMixin, Beard):
    evt_name = 'Dota'
    max_people = 5
    init_cmd = 'dota'
