import logging
import dice
import re

import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.utils import get_args

logger = logging.getLogger(__name__)


dice_faces = {
    1: "\u2680",
    2: "\u2681",
    3: "\u2682",
    4: "\u2683",
    5: "\u2684",
    6: "\u2685",
}


class DiceBeard(BeardChatHandler):

    __commands__ = [
        ("roll", 'roll',
         "Rolls dice. 0 arg: rolls 3d6. 1+ args: parses args and rolls."),
    ]

    __userhelp__ = """Rolls dice."""

    async def roll(self, msg):
        roll_text = get_args(msg, as_string=True) or "3d6"
        roll = dice.roll(roll_text)
        if re.match(r"^[0-9]+d6$", roll_text):
            text = "{} = {}".format(sum(roll),
                                    "".join(dice_faces[x] for x in roll))
        else:
            try:
                text = "{} = {}".format(sum(roll), roll)
            except TypeError:
                text = "{}".format(roll)

        await self.sender.sendMessage("{}".format(text))
