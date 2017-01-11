import functools
import re
import logging


logger = logging.getLogger(__name__)


@functools.lru_cache()
def is_key_match(url):
    # This is a circular dependency! So it must be loaded late.
    from ..apibeard import APIBeard

    match = re.match(r"/key([A-z]+)/.*", url)
    key = match.group(1)
    logger.debug("Matches found: {}".format(match))
    logger.debug("Key is: {}".format(key))
    if match:
        if key in APIBeard.allowed_keys:
            return True

    return False
