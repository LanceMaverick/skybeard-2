from .beards import Beard, BeardMethodsMixin
from telepot.aio.helper import InlineUserHandler, AnswererMixin


class BeardInlineUserHandler(InlineUserHandler,
                             AnswererMixin,
                             BeardMethodsMixin,
                             metaclass=Beard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    _timeout = 10

    __is_base_beard__ = True
