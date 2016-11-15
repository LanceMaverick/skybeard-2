import tempfile
import subprocess as sp
import logging
import re

import telepot
import telepot.aio
from skybeard.beards import BeardLoader

logger = logging.getLogger(__name__)


def is_pdf(message):
    try:
        return re.match(r".*\.pdf$", message["document"]["file_name"])
    except KeyError:
        return False

class PdfPreviewBeard(telepot.aio.helper.ChatHandler, metaclass=BeardLoader):

    # def initialise(self):
    #     # self.disp.add_handler(CommandHandler("pdfpreviewhelp", self.help))
    #     self.disp.add_handler(MessageHandler(is_pdf, send_pdf_preview))

    # __init__ is implicit

    print("hello world")
    async def send_pdf_preview(self, msg):
        logger.info("Attempting to upload photo")
        file_id = msg["document"]["file_id"]
        logger.info("Getting file from telegram")

        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            # pdf_tg_file.download(pdf_file.name)
            await self._bot.download_file(file_id, pdf_file.file)
            png_file_bytes = sp.check_output([
                "/bin/pdftoppm",
                "-singlefile",
                "-png",
                pdf_file.name
            ])

        with tempfile.NamedTemporaryFile(suffix=".png") as png_file:
            png_file.write(png_file_bytes)
            png_file.seek(0)
            sp.check_call("cp {} ~/tmp/".format(png_file.name), shell=True)
            await self.sender.sendPhoto(open(png_file.name, "rb"))

    async def on_chat_message(self, msg):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage("DEBUG: I've recieved your message")
            await self.sender.sendMessage("DEBUG: {}".format(msg))
        if is_pdf(msg):
            print("hello world")
            await self.send_pdf_preview(msg)


    def help(self, bot, update):
        update.message.reply_text(
            """TL;DR This beard shows you the first page of any pdfs it sees."""
)
