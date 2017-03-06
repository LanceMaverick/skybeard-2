import os
import re
import shutil
import importlib
import sys
import inspect
import shlex
import logging
import pip
import subprocess
import yaml
import aiohttp

import pyconfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)



def is_module(path):
    """Checks if path is a module."""

    fname, ext = os.path.splitext(path)
    if ext == ".py":
        return True
    try:
        # Python 3 allows modules not to have an __init__.py
        if any(os.path.splitext(x)[1] == ".py" for x in os.listdir(path)):
            return True
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.debug(e, 'Skipping un-recognised file or directory in plug-in path')
        pass


def contains_setup_beard_py(path):
    """Checks if path contains setup_beard.py."""

    return os.path.isfile(os.path.join(path, "setup_beard.py"))


class PythonPathContext:
    def __init__(self, path_to_add):
        self.path_to_add = path_to_add

    def __enter__(self):
        sys.path.insert(0, self.path_to_add)

    def __exit__(self, type, value, tb):
        assert sys.path[0] == self.path_to_add
        sys.path.pop(0)


def get_beard_config(config_file="../../config.yml"):
    """Attempts to load a yaml file in the beard directory.

    NOTE: The file location should be relative from where this function is
    called.

    """

    # Sometimes external libraries change the logging level. This is not
    # acceptable, so we assert after importing a beard that it has not changed.
    logger_level_before = logger.getEffectiveLevel()
    logging.debug("logging level: {}".format(logger.getEffectiveLevel()))

    callers_frame = inspect.currentframe().f_back
    logger.debug("This function was called from the file: " +
                 callers_frame.f_code.co_filename)
    base_path = os.path.dirname(callers_frame.f_code.co_filename)
    config = yaml.safe_load(open(os.path.join(base_path, config_file)))

    logging.debug("logging level: {}".format(logger.getEffectiveLevel()))
    logger_level_after = logger.getEffectiveLevel()
    assert logger_level_before == logger_level_after, \
        "Something has changed the logger level!"

    return config


def setup_beard(beard_module_name,
                *,
                beard_python_path="python",
                beard_requirements_file="requirements.txt",
                config_file="config.yml",
                example_config_file="config.yml.example",
                copy_config=False):
    """Sets up a beard for use.

    Note: beard_python_path must be a path relative to the file setup_beard is
    called from.

    """
    callers_frame = inspect.currentframe().f_back
    logger.debug("This function was called from the file: " +
                 callers_frame.f_code.co_filename)
    base_path = os.path.dirname(callers_frame.f_code.co_filename)

    if copy_config:
        if not os.path.isfile(os.path.join(base_path, config_file)):
            logger.info("Attempting to copy config file.")
            shutil.copyfile(
                os.path.join(base_path, example_config_file),
                os.path.join(base_path, config_file),
            )

    # Install requirements
    requirements_file = os.path.join(base_path, beard_requirements_file)
    if not pyconfig.get('no_auto_pip') and os.path.isfile(requirements_file):
        pip_args = [
            'pip',
            'install',
            '-r',
            # A little sanitising
            re.sub("[^a-z0-9./_]", "", requirements_file)
        ]

        if pyconfig.get('auto_pip_upgrade'):
            pip_args.append('--upgrade')

        # Using the library pip.main causes the logger level to change.
        subprocess.check_call(" ".join(pip_args), shell=True)
        # Invalidate import path cache, since it's probably changed if new
        # requirements have been installed
        importlib.invalidate_caches()

    # Import beard
    beard_python_path = os.path.join(base_path, beard_python_path)
    with PythonPathContext(beard_python_path):
        # Attempt to import the module named specified in the call to
        # setup_beard.
        #
        # Often, a module with the same name has already be imported, so the
        # module is reloaded to ensure that if a module is found in
        # beard_python_path called beard_module_name, *that* module is loaded.
        mod = importlib.import_module(beard_module_name)
        importlib.reload(mod)


def get_literal_path(path_or_autoloader):
    """Gets literal path from AutoLoader or returns input."""

    try:
        return path_or_autoloader.path
    except AttributeError:
        assert type(path_or_autoloader) is str, "beard_path is not a str or an AutoLoader!"
        return path_or_autoloader


def get_literal_beard_paths(beard_paths):
    """Returns list of literal beard paths."""

    return [get_literal_path(x) for x in beard_paths]


def all_possible_beards(paths):
    """List generator of all plug-ins that Skybeard has found and can
    be loaded"""
    literal_paths = get_literal_beard_paths(paths)

    for path in literal_paths:
        for f in os.listdir(path):
            if is_module(os.path.join(path, f)):
                yield os.path.basename(f)


def embolden(string):
    """wraps a string in bold tags"""
    return "<b>"+string+"</b>"


def italisize(string):
    """wraps a string in italic tags"""
    return "<i>"+string+"</i>"


def get_args(msg_or_text, return_string=False, **kwargs):
    """Helper function when the command used in the telegram
    chat may have arguments, e.g /command arg1 arg2.
    Returns a list of any arguments found after the command"""

    if "as_string" in kwargs:
        logger.warning(
            "as_string is being depreciated, please use return_string.")
        return_string = kwargs["as_string"]

    try:
        text = msg_or_text['text']
    except TypeError:
        text = msg_or_text

    if return_string:
        return " ".join(text.split(" ")[1:])
    else:
        return shlex.split(text)[1:]


def partition_text(text):
    """Generator for splitting long texts into ones below the
    character limit. Messages are split at the nearest line break
    and each successive chunk is yielded. Relatively untested"""
    if len(text) < 3500:
        yield text
    else:
        text_list = text.split('\n')
        l = 0                   # length iterator of current block
        i = 0                   # start position of block
        j = 0                   # end position of block

        # j scans through list of lines from start position i l tracks length
        # of all characters in the current scan If length of everything from i
        # to j+1 > the limit, yield current block, joined into single string,
        # and shift the scanning position up to the start of the new block.
        for m in text_list:
            l += len(m)
            try:
                # if adding another line will breach the limit,
                # yield current block
                if l+len(text_list[j+1]) > 3500:
                    indices = [i, j]
                    yield '\n'.join(
                            [msg for k, msg in enumerate(text_list)
                             if k in indices])
                    # shift start position for the next block
                    i = j+1
                    l = 0
                j += 1
            except IndexError:
                yield text_list[i]


BOT_JSON = None


async def getMe():
    global BOT_JSON
    if not BOT_JSON:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://api.telegram.org/bot{}/getMe".format(
                        pyconfig.get('key'))) as resp:
                BOT_JSON = (await resp.json())['result']

    return BOT_JSON
