from skybeard.beards import BeardChatHandler
from skybeard.predicates import Filters
from skybeard.utils import get_beard_config

from github import Github

CONFIG = get_beard_config()

class GithubBeard(BeardChatHandler):

    __userhelp__ = "Github. In a beard."

    # Commands takes tuples like arguments:
    # 1. Condition: Predicate function/string telegram command e.g. "dog"
    #    becomes # /dog
    # 2. Callback: Coroutine or name of member coroutine as a string to call
    #    when condition is met
    # 3. Help: Help text
    __commands__ = [
        # condition,   callback coro,             help text
        (Filters.text,     'echo',      'Echos everything said by anyone.')
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.github = Github(CONFIG['username'], CONFIG['password'])

    async def echo(self, msg):
        await self.sender.sendMessage("Github repos for {}:".format(CONFIG['username']))
        repos = ""
        for r in self.github.get_user().get_repos():
            repos += "- "+r.name+"\n"
        await self.sender.sendMessage(repos)
