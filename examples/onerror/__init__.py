from skybeard.beards import BeardChatHandler, Filters
from skybeard.decorators import onerror


class OnError(BeardChatHandler):

    __userhelp__ = "A demonstration beard for <code>@onerror</code> decorator."

    __commands__ = [
        ("onerror", 'on_error', 'Displays default <code>@onerror</code> behaviour'),
        ("fancyonerror", 'fancy_on_error', 'Displays non-default <code>@onerror</code> behaviour'),
        ("veryfancyonerror", 'very_fancy_on_error', 'Displays very non-default <code>@onerror</code> behaviour')
    ]

    @onerror
    async def on_error(self, msg):
        raise Exception

    @onerror("This is a fancy @onerror message.")
    async def fancy_on_error(self, msg):
        raise Exception

    @onerror("This is a <i>very</i> fancy <code>@onerror</code> message.",
             parse_mode="HTML")
    async def very_fancy_on_error(self, msg):
        raise Exception
