import logging
import re

logger = logging.getLogger(__name__)


def regex_predicate(pattern):
    """Returns a predicate function which returns True if pattern is matched."""
    def retfunc(chat_handler, msg):
        try:
            logging.debug("Matching regex: '{}' in '{}'".format(
                pattern, msg['text']))
            retmatch = re.match(pattern, msg['text'])
            logging.debug("Match: {}".format(retmatch))
            return retmatch
        except KeyError:
            return False

    return retfunc


# TODO make command_predicate in terms of regex_predicate
def command_predicate(cmd):
    """Returns a predicate coroutine which returns True if command is sent."""
    async def retcoro(beard_chat_handler, msg):
        bot_username = await beard_chat_handler.get_username()
        pattern = r"^/{}(?:@{}|[^@]|$)".format(
            cmd,
            bot_username,
        )
        try:
            logging.debug("Matching regex: '{}' in '{}'".format(
                pattern, msg['text']))
            retmatch = re.match(pattern, msg['text'])
            logging.debug("Match: {}".format(retmatch))
            return retmatch
        except KeyError:
            return False

    return retcoro


class Filters:
    """Filters used to call plugin methods when particular types of
    messages are received.

    For usage, see description of the BeardChatHandler.__commands__ variable.

    """
    @classmethod
    def text(cls, chat_handler, msg):
        """Filters for text messages"""
        return "text" in msg

    @classmethod
    def document(cls, chat_handler, msg):
        """Filters for sent documents"""
        return "document" in msg

    @classmethod
    def location(cls, chat_handler, msg):
        """Filters for sent locations"""
        return "location" in msg
