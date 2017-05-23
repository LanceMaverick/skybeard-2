import string
import random
import logging
from telepot import glance, message_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, BeardDBTable, ThatsNotMineException
from skybeard.decorators import onerror
from skybeard.utils import get_args
logger = logging.getLogger(__name__)

class Todo(BeardChatHandler):

    __userhelp__ = """Create a list of things to do"""

    __commands__ = [
        # command, callback coro, help text
        ("addtodo", 'add_todo', 'Add a single or a list of items to the to-do list. Delimiter: ";"'),
        ("todo", 'get_todo', 'View your to-do list'),
        ("cleartodo", 'clear_todo', 'Clear your to-do list'),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("Creating BeardDBTable.")
        self.todo_table = BeardDBTable(self, 'todos')

    @onerror()
    async def add_todo(self, msg):
        u_id = msg['from']['id']
        args = get_args(msg)
        if args:
            todo_str = ' '.join(args)
            todo_list = todo_str.split(';')
            with self.todo_table as table:
                for todo in todo_list:
                    r_id = "".join(
                            [
                                random.choice(string.ascii_letters)
                                for x in range(4)
                                ])

                    table.insert(dict(
                        uid = u_id, 
                        item = todo,
                        rid = r_id))
            await self.sender.sendMessage('To-do list updated') 
            await self.get_todo(msg)
        else:
            await self.sender.sendMessage("No arguments given.")

    async def _make_keyboard(self, items):
        inline_keyboard = []
        for item in items:
            inline_keyboard.append([
                    InlineKeyboardButton(
                        text = item['item'],
                        callback_data = self.serialize(
                            item['rid']))])
        markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        return markup

    async def _get_user_items(self, u_id):
        with self.todo_table as table:
            matches = table.find(uid = u_id)
        items = [match for match in matches]
        return items

    @onerror()
    async def get_todo(self, msg):
        u_id = msg['from']['id']
        items = await self._get_user_items(u_id)
        if not items:
            await self.sender.sendMessage('Your to-do list is empty')
            return
        keyboard = await self._make_keyboard(items)
        await self.sender.sendMessage(
            text = 'TODO list. Click an entry to delete it',
            reply_markup = keyboard)

    @onerror()
    async def clear_todo(self, msg):
        await self.sender.sendMessage('Are you sure you want to clear your to-do list? (yes/no)')
        reply = await self.listener.wait()
        if reply['text'].lower() == 'yes':
            u_id = msg['from']['id']
            with self.todo_table as table:
                matches = table.find(uid = u_id)
                for match in matches:
                    table.delete(match)
            await self.sender.sendMessage('List cleared.')
        else:
            await self.sender.sendMessage('List was not cleared.')

    @onerror()
    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')
        match = None
        try:
            data = self.deserialize(query_data)
            print(data)
            with self.todo_table as table:
                match = table.find_one(rid = data)
                table.delete(rid = data)

            #silently quit if already deleted
            if not match:
                logger.info(
                        'User {} trying to delete non-existent to-do entry with key'.format(
                            data))
                return

            #don't let other users delete your entries
            if from_id != match['uid']:
                logger.info(
                        'User {} trying to delete to-do entry for user {} with key'.format(
                            from_id, 
                            match['uid'],
                            match['id']))
                return

            items = await self._get_user_items(from_id)
            if items:
                keyboard = await self._make_keyboard(items)
                await self.bot.editMessageText(
                        message_identifier(msg['message']),
                        text = '.', 
                        reply_markup=keyboard)
                await self.bot.editMessageText(
                        message_identifier(msg['message']),
                        text = 'TODO list. Click an entry to delete it',
                        reply_markup=keyboard
                        )
            else:
                await self.bot.editMessageText(
                        message_identifier(msg['message']),
                        text = 'Your to-do list is now empty.'
                        )

        #silently except if not this beard's callback data
        except ThatsNotMineException:
            pass
        
        try:
            super().on_callback_query(msg)
        except AttributeError:
            pass




        



