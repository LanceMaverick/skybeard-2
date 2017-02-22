import pickle
import dill
from telepot import glance, message_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.bearddbtable import BeardDBTable
from skybeard.utils import get_beard_config, get_args
from skybeard.decorators import onerror
from skybeard.mixins import PaginatorMixin


from github import Github
from github.GithubException import UnknownObjectException

from . import format_

import logging

logger = logging.getLogger(__name__)

CONFIG = get_beard_config()


class GithubBeard(PaginatorMixin, BeardChatHandler):

    __userhelp__ = "Github. In a beard."

    __commands__ = [
        ("currentusersrepos", 'get_current_user_repos',
         'Lists clickable links to repos of specifed user.'),
        ("getrepo", "get_repo",
         "Gets information about given repo specifed in 1st arg."),
        ("getpr", "get_pending_pulls",
         "Gets pending pull requests from specified repo (1st arg)"),
        ("getdefaultrepo", "get_default_repo", "Gets default repo for this chat."),
        ("setdefaultrepo", "set_default_repo", "Sets default repo for this chat."),
        ("searchrepos", "search_repos", "Searches for repositories in github."),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.github = Github(CONFIG['token'])
        self.default_repo_table = BeardDBTable(self, 'default_repo')
        self.search_repos_results = BeardDBTable(self, 'search_repos_results')

    @onerror
    async def search_repos(self, msg):

        args = get_args(msg, return_string=True)
        if not args:
            await self.sender.sendMessage("No search term given")
        await self.sender.sendChatAction('typing')
        search_results = self.github.search_repositories(args)
        search_results = [i for i in search_results[:30]]

        await self.send_paginated_message(
            search_results, format_.make_repo_msg_text)

    @onerror
    async def get_default_repo(self, msg):
        with self.default_repo_table as table:
            entry = table.find_one(chat_id=self.chat_id)
            if entry:
                await self.sender.sendMessage(
                    "Default repo for this chat: {}".format(entry['repo']))
            else:
                await self.sender.sendMessage("No repo set.")

    @onerror
    async def set_default_repo(self, msg):
        args = get_args(msg)
        with self.default_repo_table as table:
            try:
                entry = table.insert(dict(chat_id=self.chat_id, repo=args[0]))
            except IndexError:
                await self.sender.sendMessage("No argument given for repo name.")
                return

            if entry:
                await self.sender.sendMessage("Repo set to: {}".format(args[0]))
            else:
                raise Exception("Not sure how, but the entry failed to be got?")

    async def user_not_found(self):
        """Send a message explaining the user was not found."""
        await self.sender.sendMessage("User not found.")

    @onerror("Failed to get repo info. No argument provided?")
    async def get_repo(self, msg):
        """Gets information about a github repo."""
        args = get_args(msg)

        repo = self.github.get_repo(args[0])
        await self.sender.sendMessage("Repo name: {}".format(repo.name))
        await self.sender.sendMessage("Repo str: {}".format(repo))

    @onerror("Failed to get repo info.")
    async def get_pending_pulls(self, msg):
        """Gets information about a github repo."""
        args = get_args(msg)
        if args:
            repo = self.github.get_repo(args[0])
        else:
            with self.default_repo_table as table:
                entry = table.find_one(chat_id=self.chat_id)
            repo = self.github.get_repo(entry['repo'])
        pull_requests = repo.get_pulls()

        pr = None
        for pr in pull_requests:
            await self.sender.sendMessage(
                await format_.make_pull_msg_text_informal(pr),
                parse_mode='HTML')
        if pr is None:
            await self.sender.sendMessage(
                "No pull requests found for {}.".format(repo.name))

    @onerror
    async def get_current_user_repos(self, msg):
        args = get_args(msg)
        try:
            try:
                user = self.github.get_user(args[0])
            except IndexError:
                user = self.github.get_user()
        except UnknownObjectException:
            await self.user_not_found()
            return

        name = user.name or user.login
        await self.sender.sendMessage("Github repos for {}:".format(name))
        await self.sender.sendChatAction(action="typing")
        repos = ""
        for r in user.get_repos():
            repos += "- <a href=\"{}\">{}</a>\n".format(r.url, r.name)
        await self.sender.sendMessage(repos, parse_mode='HTML')
