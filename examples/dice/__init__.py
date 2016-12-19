import logging
import dice
import re

import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)

def get_args(msg_text):
    return msg_text.split(" ")[1:]

#user unicode characters of dice faces
dice_faces = {
    1: "\u2680",
    2: "\u2681",
    3: "\u2682",
    4: "\u2683",
    5: "\u2684",
    6: "\u2685",
}

class DiceBeard(BeardChatHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #register command which calls self.roll function
        self.register_command("roll", self.roll)

    async def roll(self, msg):
        roll_text = " ".join(get_args(msg['text'])) or "3d6"
        roll = dice.roll(roll_text)
        if re.match(r"^[0-9]d6$", roll_text):
            text = "{} = {}".format(sum(roll),
                                    "".join(dice_faces[x] for x in roll))
        else:
            try:
                text = "{} = {}".format(sum(roll), roll)
            except TypeError:
                text = "{}".format(roll)

        await self.sender.sendMessage("{}".format(text))

__userhelp__ = """Rolls dice."""
