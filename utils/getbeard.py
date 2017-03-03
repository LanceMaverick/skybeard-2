#!/usr/bin/env python
import argparse
import yaml

import git


def download_beard(beard_name, upgrade):
    beard_details = yaml.load(open("beard_repo/{}.yml".format(beard_name)))
    git_ = git.Git("beard_cache")
    print("Attempting to clone {}...".format(beard_details['git_url']))
    try:
        git_.clone(beard_details['git_url'])
        print("Done!")
    except git.GitCommandError:
        repo = git.Repo("beard_cache/{}".format(beard_name))
        if upgrade:
            print("Updating repo")
            # TODO make it not rely on being origin
            repo.remotes.origin.pull()
            print("Done!")
        else:
            print("Repo already exists. Nothing done")


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
