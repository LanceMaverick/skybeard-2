"""The purpose of this test is too test that the config and beards imports
properly before the bot is run."""
import os
import yaml
import unittest
import importlib
import pyconfig
from skybeard.utils import PythonPathContext


class TestConfig(unittest.TestCase):
    def test_import_all_beards_return_None(self):

        pyconfig.set('config_file', os.path.abspath('config.yml.example'))
        with open(pyconfig.get('config_file')) as config_file:
            for k, v in yaml.load(config_file).items():
                pyconfig.set(k, v)
        beard_paths = pyconfig.get('beard_paths')
        pyconfig.set('beard_paths', [os.path.expanduser(x) for x in beard_paths])
        stache_paths = pyconfig.get('stache_paths')
        pyconfig.set('stache_paths', [os.path.expanduser(x) for x in stache_paths])

        for path in pyconfig.get('beard_paths'):
            with PythonPathContext(path):
                for beard in pyconfig.get('beards'):
                    try:
                        importlib.import_module(beard)
                    except ImportError:
                        pass

        # Once the modules are imported (or not), reimporting will return only
        # the module. If we get an ImportError here, then one of them has gone
        # wrong

        successfully_imported_modules = []
        import_exceptions = []
        for beard in pyconfig.get('beards'):
            try:
                mod = importlib.import_module(beard)
                successfully_imported_modules.append(mod)
            except ImportError as e:
                import_exceptions.append(e)

        if import_exceptions:
            self.fail("We got problems: {}".format("\n".join(str(e) for e in import_exceptions)))


if __name__ == '__main__':

    unittest.main()
