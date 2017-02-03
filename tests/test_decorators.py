import asyncio
import unittest
import types
import functools
from skybeard import decorators


class TestSkybeardDecorators(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_onerror_with_args_return_None(self):
        @decorators.onerror("<i>foo</i>", parse_mode="HTML")
        async def foo(beard, *args, **kwargs):
            return beard, args, kwargs

        foo_coro = foo(None)

        self.assertIsInstance(foo, types.FunctionType)
        self.assertIsInstance(foo_coro, types.CoroutineType)

        self.loop.run_until_complete(foo_coro)

    def test_debugonly_return_None(self):
        @decorators.debugonly("<i>foo</i>", parse_mode="HTML")
        async def foo(beard, *args, **kwargs):
            return beard, args, kwargs

        foo_coro = foo(None)

        self.assertIsInstance(foo, types.FunctionType)
        self.assertIsInstance(foo_coro, types.CoroutineType)

        self.loop.run_until_complete(foo_coro)


if __name__ == '__main__':
    unittest.main()
