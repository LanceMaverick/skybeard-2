from skybeard.beards import BeardChatHandler
from skybeard.predicates import Filters
from skybeard.utils import get_beard_config, get_args
from skybeard.decorators import onerror

from github import Github
import maya

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
        ("currentusersrepos",     'get_current_user_repos',      'Echos everything said by anyone.'),
        ("getrepo", "get_repo", "Gets information about given repo specifed in 1st arg."),
        ("getpr", "get_pending_pulls", "Gets pending pull requests from specified repo (1st arg)"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.github = Github(CONFIG['token'])

    @onerror("Failed to get repo info. No argument provided?")
    async def get_repo(self, msg):
        """Gets information about a github repo."""
        args = get_args(msg)

        repo = self.github.get_repo(args[0])
        await self.sender.sendMessage("Repo name: {}".format(repo.name))
        await self.sender.sendMessage("Repo str: {}".format(repo))

    async def make_pull_msg_text(self, pull):
        retval = ""
        retval += "<b>Title</b>: {}\n".format(pull.title)
        retval += "<b>Created at</b>: {}\n".format(pull.created_at)
        retval += "<b>Body</b>: {}\n".format(pull.body)

        return retval

    async def make_pull_msg_text_informal(self, pull):
        retval = "<b>Pull request {} for {}</b>\n\n".format(pull.number, pull.base.repo.name)
        retval += "{} (created {})\n".format(pull.title, maya.MayaDT.from_datetime(pull.created_at).slang_date())
        if pull.body:
            retval += "{}\n".format(pull.body)
        retval += "\n{}".format(pull.url)

        return retval

    @onerror("Failed to get repo info. No argument provided?")
    async def get_pending_pulls(self, msg):
        """Gets information about a github repo."""
        args = get_args(msg)

        repo = self.github.get_repo(args[0])
        pull_requests = repo.get_pulls()
        for pr in pull_requests:
            await self.sender.sendMessage(await self.make_pull_msg_text_informal(pr), parse_mode='HTML')

    @onerror
    async def get_current_user_repos(self, msg):
        args = get_args(msg)
        try:
            user = self.github.get_user(args[0])
        except IndexError:
            user = self.github.get_user()
        name = user.name or user.login
        await self.sender.sendMessage("Github repos for {}:".format(name))
        await self.sender.sendChatAction(action="typing")
        repos = ""
        for r in user.get_repos():
            repos += "- <a href=\"{}\">{}</a>\n".format(r.url, r.name)
        await self.sender.sendMessage(repos, parse_mode='HTML')
