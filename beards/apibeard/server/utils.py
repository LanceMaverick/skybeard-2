import functools
import re
import logging

from .. import APIBeard

logger = logging.getLogger(__name__)


@functools.lru_cache()
def is_key_match(url):
    match = re.match(r"/key([A-z]+)/.*", url)
    key = match.group(1)
    logger.debug("Matches found: {}".format(match))
    logger.debug("Key is: {}".format(key))
    if match:
        if key in APIBeard.allowed_keys:
            return True

    return False
