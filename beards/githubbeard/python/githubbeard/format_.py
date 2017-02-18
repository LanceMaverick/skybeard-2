import maya


async def make_pull_msg_text(pull):
    """Creates basic message text for pull request."""
    retval = ""
    retval += "<b>Title</b>: {}\n".format(pull.title)
    retval += "<b>Created at</b>: {}\n".format(pull.created_at)
    retval += "<b>Body</b>: {}\n".format(pull.body)

    return retval


async def make_pull_msg_text_informal(pull):
    """Creates informal message text for pull request."""
    retval = "<b>Pull request {} for {}</b>\n\n".format(
        pull.number, pull.base.repo.name)
    retval += "{} (created {})\n".format(
        pull.title,
        maya.MayaDT.from_datetime(pull.created_at).slang_date())
    if pull.body:
        retval += "{}\n".format(pull.body)
    retval += "\n{}".format(pull.url)

    return retval


async def make_repo_msg_text(repo):
    """Creates message text for repo"""
    retval = "<b>Repository:</b> {}\n".format(repo.full_name)
    if repo.description:
        retval += "<b>Description:</b> {}\n".format(repo.description.split("\n")[0].split(".")[0])
    retval += "<b>Url:</b> {}".format(repo.html_url)

    return retval
