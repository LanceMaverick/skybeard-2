from pygithub3 import Github
import yaml

from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror
from skybeard.utils import get_args


class RepoHelper(BeardChatHandler):

    __userhelp__ = """Helps make yamls for beard repository."""

    __commands__ = [
        ("makerepoyamlfromgithub", 'make_repo_yaml',
         'Makes yaml for repo based on github repo name.')
    ]

    # __init__ is implicit

    @onerror
    async def make_repo_yaml(self, msg):
        args = get_args(msg)
        try:
            repo_name = args[0]
        except IndexError:
            await self.sender.sendMessage(
                "Please provide the full name of the repo.")
            resp = await self.listener.wait()
            repo_name = resp['text']

        await self.sender.sendChatAction("upload_document")

        gh = Github()
        repo = gh.get_repo(repo_name)
        data = {
            "name": repo.name,
            "description": repo.description,
            "git_url": repo.clone_url
        }

        name = "{}.yml".format(data["name"])
        encoded_data = yaml.dump(data,
                                 encoding="utf-8",
                                 default_flow_style=False)
        self.logger.debug("Yaml made:\n\n{}".format(
            encoded_data.decode('utf-8')))
        await self.sender.sendDocument((name, encoded_data))
