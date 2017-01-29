import asyncio
import unittest

import telepot
import telepot.aio

from skybeard import predicates
from skybeard.beards import BeardChatHandler

# TODO make TestBeard to test with real Telegram messages


class TestBeard(BeardChatHandler):
    pass


class TestChatHandler():
    def __init__(self, username, *args, **kwargs):
        self._username = username

    async def get_username(self):
        return self._username


class TestSkybeardPredicates(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_regex_predicate_return_None(self):
        f = predicates.regex_predicate("^foo.*")
        msg = {"text": "foobar"}
        self.assertTrue(f(None, msg))
        msg = {"text": "bar"}
        self.assertFalse(f(None, msg))

    def test_command_predicate_return_None(self):
        async def coro():
            f = predicates.command_predicate("foobar")
            c = TestChatHandler("foobot")
            msg = {"text": "/foobar"}
            self.assertTrue(await f(c, msg))
            msg = {"text": "/foobar@foobot"}
            self.assertTrue(await f(c, msg))
        self.loop.run_until_complete(coro())

    def test_Filters_text_return_None(self):
        msg = {"text": "foobar"}
        self.assertTrue(predicates.Filters.text(None, msg))

    def test_Filters_location_return_None(self):
        # TODO check the form of location messages
        msg = {"location": [234, -1234]}
        self.assertTrue(predicates.Filters.location(None, msg))

    def test_Filters_document_return_None(self):
        # TODO check the form of document messages
        msg = {"document": b"asdfoinapofjapodifj"}
        self.assertTrue(predicates.Filters.document(None, msg))


if __name__ == '__main__':
    unittest.main()
