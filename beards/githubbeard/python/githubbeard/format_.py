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
