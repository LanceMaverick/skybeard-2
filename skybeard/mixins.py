import logging

import dill
from telepot import glance, message_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from .beards import ThatsNotMineException
from .bearddbtable import BeardDBTable

logger = logging.getLogger(__name__)


class PaginatorMixin:
    """Mixin to provide paginated messages.

    To use, inherit on the left, e.g.

    .. code:: python
        class FooBeard(PaginatorMixin, BeardChatHandler):
            # etc.

    To send a paginated message, use `self.send_paginated_message`.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paginator_table = BeardDBTable(self, '_paginator')

    async def __make_prev_next_keyboard(self, prev_seq, next_seq):
        """Makes next/prev keyboard for paginated message."""
        inline_keyboard = []
        if len(prev_seq) > 0:
            inline_keyboard.append(
                InlineKeyboardButton(
                    text="« prev",
                    callback_data=self.serialize('p')))
        if len(next_seq) > 0:
            inline_keyboard.append(
                InlineKeyboardButton(
                    text="next »",
                    callback_data=self.serialize('n')))

        return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])

    async def send_paginated_message(
            self,
            next_seq,
            formatter,
            curr_item=None,
            prev_seq=None,
    ):
        """Sends paginated message.

        This function takes the current item, iterators for previous and next
        items and a formatter function that changes items into strings.

        Args:
            next_seq: The iterator for next items (must be sliceable).
            formatter: The function that changes items into strings.
            curr_item: The item you want initally displayed on the message.
                Defaults to first element of next_seq.
            prev_seq: The iterator for previous items (must be sliceable).
                Defaults to empty list.
        """
        if curr_item is None:
            curr_item = next_seq[0]
            next_seq = next_seq[1:]
        if prev_seq is None:
            prev_seq = []

        keyboard = await self.__make_prev_next_keyboard(prev_seq, next_seq)
        sent_msg = await self.sender.sendMessage(
            await formatter(curr_item),
            parse_mode='HTML',
            reply_markup=keyboard
        )

        with self._paginator_table as table:
            entry_to_insert = {
                'message_id': sent_msg['message_id'],
                'prev_seq': dill.dumps(prev_seq),
                'curr_item': dill.dumps(curr_item),
                'next_seq': dill.dumps(next_seq),
                'formatter_func': dill.dumps(formatter)
            }
            table.insert(entry_to_insert)

    async def on_callback_query(self, msg):
        """Uses data `'n'` and `'p'` to signal message page turn."""
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)

            if data == 'n' or data == 'p':
                with self._paginator_table as table:
                    entry = table.find_one(
                        message_id=msg['message']['message_id'],
                    )
                self.logger.debug("Got entry for message id: {}".format(
                    entry['message_id']))

                logger.debug("Loading prev_seq...")
                prev_seq = dill.loads(entry['prev_seq'])
                logger.debug("Loading curr_item...")
                curr_item = dill.loads(entry['curr_item'])
                logger.debug("Loading next_seq...")
                next_seq = dill.loads(entry['next_seq'])
                logger.debug("Loading formatter_func...")
                formatter_func = dill.loads(entry['formatter_func'])
                logger.debug("Un-dill-ed all objects.")

                if data == 'p':
                    logger.debug("Getting previous item.")
                    next_seq.insert(0, curr_item)
                    curr_item = prev_seq[-1]
                    prev_seq = prev_seq[:-1]
                if data == 'n':
                    logger.debug("Getting next item.")
                    prev_seq.append(curr_item)
                    curr_item = next_seq[0]
                    next_seq = next_seq[1:]

                keyboard = await self.__make_prev_next_keyboard(
                    prev_seq, next_seq)

                await self.bot.editMessageText(
                    message_identifier(msg['message']),
                    await formatter_func(curr_item),
                    parse_mode='HTML',
                    reply_markup=keyboard
                )

                logger.debug("Updating prev_seq entry.")
                entry['prev_seq'] = dill.dumps(prev_seq)
                logger.debug("Updating curr_item entry.")
                entry['curr_item'] = dill.dumps(curr_item)
                logger.debug("Updating next_seq entry.")
                entry['next_seq'] = dill.dumps(next_seq)
                logger.debug("Updating entry in database.")
                with self._paginator_table as table:
                    table.update(entry, ['message_id'])
                logger.debug("Entry updated.")

        except ThatsNotMineException:
            pass

        try:
            super().on_callback_query(msg)
        except AttributeError:
            pass
