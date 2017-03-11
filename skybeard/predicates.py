import types
import logging
import re

logger = logging.getLogger(__name__)


def regex_predicate(pattern, lower=False):
    """Returns a predicate function which returns True if pattern is matched.
        if lower == True, the text will be made lower case."""

    compiled_pattern = re.compile(pattern, re.IGNORECASE if lower else 0)

    def retfunc(chat_handler, msg):
        try:
            # if lower:
            #     text = msg['text'].lower()
            # else:
            #     text = msg['text']
            text = msg['text']
            logger.debug("Matching regex: '{}' in '{}'".format(
                pattern, text))
            retmatch = compiled_pattern.match(text)
            logger.debug("Match: {}".format(retmatch))
            return retmatch
        except KeyError:
            return False

    def _toJSON(self):
        return str(compiled_pattern)

    retfunc.toJSON = types.MethodType(_toJSON, retfunc)

    return retfunc


# TODO make command_predicate in terms of regex_predicate
def command_predicate(cmd):
    """Returns a predicate coroutine which returns True if command is sent."""
    async def retcoro(beard_chat_handler, msg):
        bot_username = await beard_chat_handler.get_username()
        pattern = r"^/{}(?:@{}| |$)".format(
            cmd,
            bot_username,
        )
        try:
            logger.debug("Matching regex: '{}' in '{}'".format(
                pattern, msg['text']))
            retmatch = re.match(pattern, msg['text'])
            logger.debug("Match: {}".format(retmatch))
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
    def text_no_cmd(cls, chat_handler, msg):
        """Filters for text messages that don't
        start with a bot command"""
        return "text" in msg and not msg["text"].startswith("/")

    @classmethod
    def document(cls, chat_handler, msg):
        """Filters for sent documents"""
        return "document" in msg

    @classmethod
    def location(cls, chat_handler, msg):
        """Filters for sent locations"""
        return "location" in msg
