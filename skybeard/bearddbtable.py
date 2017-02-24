import string
import random
import os
import logging
import dataset

import pyconfig

logger = logging.getLogger(__name__)


class BeardDBTable(object):
    """Placeholder for database object for beards.

    For use with `with`.

    If per_instance is False, then the database table is per class, rather than
    per instance.

    """
    def __init__(self, beard, table_name, per_instance=False, **kwargs):
        self.beard_name = type(beard).__name__
        if per_instance:
            self.table_name = "{}_{}_{}".format(
                self.beard_name,
                beard.chat_id,
                table_name
            )
        else:
            self.table_name = "{}_{}".format(
                self.beard_name,
                table_name
            )
        self.kwargs = kwargs

    def __enter__(self):
        self.db = dataset.connect(pyconfig.get('db_url'))
        self.db.__enter__()
        self.table = self.db.get_table(self.table_name, **self.kwargs)
        logger.debug(
            "BeardDBTable initalised with: self.table: {}, self.db: {}".format(
                self.table, self.db))
        return self

    def __exit__(self, error_type, error_value, traceback):
        self.db.__exit__(error_type, error_value, traceback)

        del self.table
        del self.db

    def __getattr__(self, name):
        """If the normal getattr fails, try getattr(self.table, name)."""
        try:
            assert self.table
        except AttributeError as e:
            raise AttributeError(
                "Open table not found. Are you using BeardDBTable with with?")

        return getattr(self.table, name)


async def make_binary_entry_filename(table, key):
    # Assume the random string has been found, until it's not been found.
    random_string_found = True
    while random_string_found:
        random_string = "".join(
            [random.choice(string.ascii_letters) for x in range(50)])
        for d in os.listdir(pyconfig.get('db_bin_path')):
            if random_string in d:
                break
        else:
            random_string_found = False

    primary_key = "_".join(table.table.table.primary_key.columns.keys())

    return os.path.join(
        pyconfig.get('db_bin_path'), "{}_{}_{}_{}.dbbin".format(
            table.table_name,
            primary_key,
            key,
            random_string))
