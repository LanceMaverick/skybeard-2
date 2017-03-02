#!/usr/bin/env python

import argparse
from pathlib import Path

import stringcase


def make_readme(dir_, name):
    readme_text = """A beard named {} for skybeard-2.""".format(name)
    with (dir_ / Path("README.txt")).open("w") as f:
        f.write(readme_text)


def make_init(dir_, name):
    python_path = dir_ / Path("python/{}".format(name))
    python_path.mkdir(parents=True)
    init_text = '''
from skybeard.beards import BeardChatHandler
from skybeard.decorators import onerror
from skybeard.utils import get_args


class {beardclassname}(BeardChatHandler):

    __userhelp__ = """Default help message."""

    __commands__ = [
        # command, callback coro, help text
        ("echo", 'echo', 'Echos arguments. e.g. <code>/echo [arg1 [arg2 ... ]]</code>')
    ]

    # __init__ is implicit

    @onerror
    async def echo(self, msg):
        args = get_args(msg)
        if args:
            await self.sender.sendMessage("Args: {{}}".format(args))
        else:
            await self.sender.sendMessage("No arguments given.")

    '''.strip().format(beardclassname=stringcase.pascalcase(name))

    with (python_path / Path("__init__.py")).open("w") as f:
        f.write(init_text)


def make_setup_beard(dir_, name):
    setup_beard_text = '''
from skybeard.utils import setup_beard

setup_beard(
    "{}",
)

    '''.format(name).strip()

    with (dir_ / Path("setup_beard.py")).open("w") as f:
        f.write(setup_beard_text)


def make_requirements(dir_, requirements):
    requirements_text = "\n".join(requirements)

    with (dir_ / Path("requirements.txt")).open("w") as f:
        f.write(requirements_text)


def main():
    parser = argparse.ArgumentParser(
        description='Create new beard in given folder.')
    parser.add_argument('name', help="Name of beard.")
    parser.add_argument(
        '-d', '--dir', type=Path, default=None,
        help="Directory to put beard in (defaults to beard name).")
    parser.add_argument(
        '-r', '--requirements', default=None,
        help="Create requirements file with optional requirements.", nargs="*")

    parsed = parser.parse_args()

    if parsed.dir is None:
        parsed.dir = Path(parsed.name)

    try:
        parsed.dir.mkdir(parents=True)
    except FileExistsError:
        pass

    make_readme(parsed.dir, parsed.name)
    make_init(parsed.dir, parsed.name)
    make_setup_beard(parsed.dir, parsed.name)
    if parsed.requirements is not None:
        make_requirements(parsed.dir, parsed.requirements)


if __name__ == '__main__':
    main()
