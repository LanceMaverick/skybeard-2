#!/usr/bin/env python
import argparse
import yaml
import os
from os.path import join
from pathlib import Path

import git


class NoRecordFound(Exception):
    pass


def find_record(beard_name):
    p = Path("beard_repo")
    yamls = p.glob("*.yml")
    for y in yamls:
        record = yaml.load(y.open())
        if record['name'] == beard_name:
            return record
    else:
        raise NoRecordFound("No record found for beard named: "+beard_name)


def download_beard(beard_name, upgrade):
    beard_details = find_record(beard_name)
    git_ = git.Git("beard_cache")
    print("Attempting to clone from {}...".format(beard_details['git_url']))
    try:
        repo_dir = join("beard_cache", beard_name)
        os.makedirs(repo_dir)
        repo = git.Repo()
        repo.clone_from(beard_details['git_url'], repo_dir)
        print("Done!")
    except FileExistsError:
        repo = git.Repo("beard_cache/{}".format(beard_name))
        if upgrade:
            print("Updating repo")
            # Should be origin, since no-one should add another remote.
            repo.remotes.origin.pull()
            print("Done!")
        else:
            print("Repo already exists. Nothing to do.")


def main():
    parser = argparse.ArgumentParser(
        description='Gets beards from the internet! Like magic!')
    parser.add_argument('beard_name', help="Name of beard to get")
    parser.add_argument('-U', '--upgrade', action="store_true",
                        default=False)

    parsed = parser.parse_args()

    download_beard(parsed.beard_name, parsed.upgrade)


if __name__ == '__main__':
    main()
