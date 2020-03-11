#!/usr/bin/env python3

import logging
import requests
import subprocess

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext






def main():
    updater = Updater("971322549:AAHwgjKp-_i4qbimcSAenYpD_I8CI87uClk", use_context=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start_sync", start_sync))
    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()



def start_sync(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! I\'m a Komodo QA department Telegram bot.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')



if __name__ == '__main__':
    main()