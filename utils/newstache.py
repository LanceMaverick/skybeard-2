#!/usr/bin/env python

import argparse
from pathlib import Path

from utils import make_init_text


def make_file(name, filename=None):
    if filename is not None:
        path = Path(filename)
    else:
        path = Path(name+".py")

    init_text = make_init_text(name)

    with path.open("w") as f:
        f.write(init_text)

    print("Moustache created as: {}".format(str(path)))


def main():
    parser = argparse.ArgumentParser(
        description='Create new moustache.')
    parser.add_argument('name', help="Name of beard.")
    parser.add_argument('-f', '--filename', type=str, default=None,
                        help="Optionally specify filename.")

    parsed = parser.parse_args()
    make_file(parsed.name, parsed.filename)


if __name__ == '__main__':
    main()
