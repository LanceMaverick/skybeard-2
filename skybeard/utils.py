import os
import shlex
import logging

logger = logging.getLogger(__name__)


def is_module(path):
    """Checks if path is a module."""

    fname, ext = os.path.splitext(path)
    if ext == ".py":
        return True
    elif os.path.exists(os.path.join(path, "__init__.py")):
        return True
    else:
        return False


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
