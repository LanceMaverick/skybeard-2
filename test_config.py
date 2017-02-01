"""The purpose of this test is too test that the config and beards imports
properly before the bot is run."""
import unittest
import importlib
from skybeard.utils import PythonPathContext

import config

class TestConfig(unittest.TestCase):
    def test_import_all_beards_return_None(self):
        for path in config.beard_paths:
            with PythonPathContext(path):
                for beard in config.beards:
                    try:
                        importlib.import_module(beard)
                    except ImportError:
                        pass

        # Once the modules are imported (or not), reimporting will return only
        # the module. If we get an ImportError here, then one of them has gone
        # wrong

        successfully_imported_modules = []
        import_exceptions = []
        for beard in config.beards:
            try:
                mod = importlib.import_module(beard)
                successfully_imported_modules.append(mod)
            except ImportError as e:
                import_exceptions.append(e)

        if import_exceptions:
            self.fail("We got problems: {}".format("\n".join(str(e) for e in import_exceptions)))


if __name__ == '__main__':
    unittest.main()
