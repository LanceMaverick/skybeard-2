import subprocess as sp
import os
import shutil
import tempfile
import logging

logger = logging.getLogger(__name__)

class AutoLoader(object):
    """Base class for automatic loaders (e.g. Git)"""
    pass

class Git(AutoLoader):
    def __init__(self, url, import_as=None, branch=None):
        "Creates a temporary directory full of a git repo."

        self.url = url
        logger.debug("Creating temporary directory")
        self.path = tempfile.mkdtemp()
        logger.info("Importing {} using git".format(self.url))
        git_cmd ="/usr/bin/git -C {dir} clone {url}".format(dir=self.path, url=self.url).split(" ") 
        if import_as is not None:
            git_cmd.append(import_as)
        if branch is not None:
            git_cmd.extend(["-b", branch])

        sp.check_call(git_cmd)

    def __del__(self):
        logger.debug("Deleting temporary directory {}".format(self.path))
        shutil.rmtree(self.path)

