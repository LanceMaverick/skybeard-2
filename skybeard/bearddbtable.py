import logging
import dataset

import pyconfig

logger = logging.getLogger(__name__)


class BeardDBTable(object):
    """Placeholder for database object for beards.

    For use with async with.

    """
    def __init__(self, beard, table_name, **kwargs):
        self.beard_name = type(beard).__name__
        self.table_name = "{}_{}".format(
            self.beard_name,
            table_name
        )
        self.kwargs = kwargs

    def __enter__(self):
        self.db = dataset.connect(pyconfig.get('db_url'))
        self.db.__enter__()
        self.table = self.db.get_table(self.table_name, **self.kwargs)
        logger.debug("BeardDBTable initalised with: self.table: {}, self.db: {}".format(
            self.table, self.db))
        return self

    def __exit__(self, error_type, error_value, traceback):
        self.db.__exit__(error_type, error_value, traceback)

        del self.table
        del self.db

    def __getattr__(self, name):
        """If the normal getattr fails, try getattr(self.table, name)."""
        try:
            return getattr(self.table, name)
        except AttributeError:
            raise AttributeError(
                "Open table not found. Are you using BeardDBTable with with?")
