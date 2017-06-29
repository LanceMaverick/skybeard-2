import telepot
from skybeard.beardinlineuserhandler import BeardInlineUserHandler


class InlineHandler(BeardInlineUserHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, query_string = telepot.glance(
                msg,
                flavor='inline_query'
            )
            print(self.id, ':', 'Inline Query:', query_id, from_id, query_string)

            articles = [{'type': 'article',
                         'id': 'abc',
                         'title': query_string,
                         'message_text': query_string}]

            return articles

        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        from pprint import pprint
        pprint(msg)
        result_id, from_id, query_string = telepot.glance(
            msg,
            flavor='chosen_inline_result'
        )
        print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)
