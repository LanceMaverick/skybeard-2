import unittest
from skybeard import utils


class TestSkybeardUtils(unittest.TestCase):
    def test_is_module_return_None(self):
        self.assertTrue(utils.is_module("skybeard"))
        self.assertFalse(utils.is_module("foobarnotamodule"))

    def test_embolden_return_string(self):
        self.assertTrue(utils.embolden("foo") == "<b>foo</b>")

    def test_italisize_return_string(self):
        self.assertTrue(utils.italisize("foo") == "<i>foo</i>")

    def test_get_args_take_msg_return_None(self):
        msg = {"text": "/foobar foo bar"}
        args = utils.get_args(msg)
        expected_args = ("foo", "bar")
        self.assertTrue(all((x == y for x, y in zip(args, expected_args))))

    def test_get_args_take_text_return_None(self):
        text = "/foobar foo bar"
        args = utils.get_args(text)
        expected_args = ("foo", "bar")
        self.assertTrue(all((x == y for x, y in zip(args, expected_args))))

    def test_get_args_with_shlex_take_msg_return_None(self):
        msg = {"text": "/foobar 'foo bar' baz"}
        args = utils.get_args(msg)
        expected_args = ("foo bar", "baz")
        self.assertTrue(all((x == y for x, y in zip(args, expected_args))))

    def test_get_args_with_shlex_take_text_return_None(self):
        text =  "/foobar 'foo bar' baz"
        args = utils.get_args(text)
        expected_args = ("foo bar", "baz")
        self.assertTrue(all((x == y for x, y in zip(args, expected_args))))

    def test_partition_text_return_None(self):
        text = "a"*3000+"\n"+"b"*3000
        partitioned_text = [x for x in utils.partition_text(text)]
        self.assertTrue(len(partitioned_text) == 2)


if __name__ == '__main__':
    unittest.main()
