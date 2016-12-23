import os
import shlex

def is_module(filename):
    fname, ext = os.path.splitext(filename)
    if ext == ".py":
        return True
    elif os.path.exists(os.path.join(filename, "__init__.py")):
        return True
    else:
        return False


def get_literal_path(path_or_autoloader):
    try:
        return path_or_autoloader.path
    except AttributeError:
        assert type(path_or_autoloader) is str, "beard_path is not a str or an AutoLoader!"
        return path_or_autoloader


def get_literal_beard_paths(beard_paths):
    return [get_literal_path(x) for x in beard_paths]


def all_possible_beards(paths):
    literal_paths = get_literal_beard_paths(paths)

    for path in literal_paths:
        for f in os.listdir(path):
            if is_module(os.path.join(path, f)):
                yield os.path.basename(f)


def embolden(string):
    return "<b>"+string+"</b>"


def italisize(string):
    return "<i>"+string+"</i>"


def get_args(msg_or_text, as_string=False):
    try:
        text = msg_or_text['text']
    except TypeError:
        text = msg_or_text

    if as_string:
        return " ".join(text.split(" ")[1:])
    else:
        return shlex.split(text)[1:]
