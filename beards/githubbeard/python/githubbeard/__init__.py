
import pickle
from telepot import glance, message_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.bearddbtable import BeardDBTable
from skybeard.utils import get_beard_config, get_args
from skybeard.decorators import onerror, debugonly


from github import Github
from github.GithubException import UnknownObjectException

from . import format_

import logging

logger = logging.getLogger(__name__)

CONFIG = get_beard_config()


class PaginatorMixin:
    def __make_prev_next_keyboard(self, prev_iter, next_iter):
        inline_keyboard = []
        if len(prev_iter) > 0:
            inline_keyboard.append(
                InlineKeyboardButton(
                    text="« prev",
                    callback_data=self.serialize('p')))
        if len(next_iter) > 0:
            inline_keyboard.append(
                InlineKeyboardButton(
                    text="next »",
                    callback_data=self.serialize('n')))

        return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])


class GithubBeard(BeardChatHandler, PaginatorMixin):

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

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
        except ThatsNotMineException:
            pass

        if data == 'n' or data == 'p':
            with self.search_repos_results as table:
                entry = table.find_one(
                    message_id=msg['message']['message_id'],
                    chat_id=self.chat_id,
                )
            self.logger.debug("Got entry for message id: {}".format(entry['message_id']))

            search_results_prev = pickle.loads(entry['search_results_prev'])
            search_result_curr = pickle.loads(entry['search_result_curr'])
            search_results_next = pickle.loads(entry['search_results_next'])

            if data == 'p':
                search_results_next.insert(0, search_result_curr)
                search_result_curr = search_results_prev[-1]
                search_results_prev = search_results_prev[:-1]
            if data == 'n':
                search_results_prev.append(search_result_curr)
                search_result_curr = search_results_next[0]
                search_results_next = search_results_next[1:]


            entry['search_results_prev'] = pickle.dumps(search_results_prev)
            entry['search_result_curr'] = pickle.dumps(search_result_curr)
            entry['search_results_next'] = pickle.dumps(search_results_next)
            with self.search_repos_results as table:
                table.update(entry, ['chat_id', 'message_id'])

            keyboard = self._PaginatorMixin__make_prev_next_keyboard(search_results_prev, search_results_next)

            await self.bot.editMessageText(
                message_identifier(msg['message']),
                await format_.make_repo_msg_text(search_result_curr),
                parse_mode='HTML',
                reply_markup=keyboard
            )

    @onerror
    async def search_repos(self, msg):

        args = get_args(msg, return_string=True)
        if not args:
            await self.sender.sendMessage("No search term given")
        search_results = self.github.search_repositories(args)
        search_results = [i for i in search_results[:30]]
        sr = search_results[0]
        keyboard = self._PaginatorMixin__make_prev_next_keyboard([], search_results)
        sent_msg = await self.sender.sendMessage(
            await format_.make_repo_msg_text(sr),
            parse_mode='HTML',
            reply_markup=keyboard
        )

        with self.search_repos_results as table:
            entry_to_insert = dict(
                message_id=sent_msg['message_id'],
                chat_id=self.chat_id,
                search_results_prev=pickle.dumps([]),
                search_result_curr=pickle.dumps(search_results[0]),
                search_results_next=pickle.dumps(search_results[1:])
            )
            self.logger.debug("Inserting entry for message id: {}".format(msg['message_id']))
            self.logger.debug("Inserting entry with search_results: {}".format(search_results))
            table.insert(entry_to_insert)

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
