#!/usr/bin/env python3

import logging
import requests
import subprocess
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def main():
    updater = Updater("971322549:AAHwgjKp-_i4qbimcSAenYpD_I8CI87uClk", use_context=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("start_sync", start_sync))
    dp.add_handler(CommandHandler("start_sync_all", start_sync_all))
    dp.add_handler(CommandHandler("stop_sync", stop_sync))
    dp.add_handler(CommandHandler("stop_sync_all", stop_sync_all))
    dp.add_handler(CommandHandler("setup_binary", setup_binary))
    dp.add_handler(CommandHandler("get_current_sync_status", get_current_sync_status))
    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def get_current_sync_status(update, context):
    msg = requests.get('http://95.217.134.179/sync_stats_all').json()
    update.message.reply_text(msg)


def setup_binary(update, context):
    """Send a message when the command /start_sync is issued."""
    link = context.args
    msg = requests.post('http://95.217.134.179/upload_binary', data=link).json()
    update.message.reply_text(msg)



def start_sync(update, context):
    """Send a message when the command /start_sync is issued."""

    for ticker in context.args:
        msg = requests.get('http://95.217.134.179/sync_start/{}'.format(ticker)).json()
    update.message.reply_text(msg)


def stop_sync(update, context):
    """Send a message when the command /start_sync is issued."""

    for ticker in context.args:
        msg = requests.get('http://95.217.134.179/sync_stop/{}'.format(ticker)).json()
    update.message.reply_text(msg)


def start_sync_all(update, context):
    """Send a message when the command /start_sync is issued."""

    msg = requests.get('http://95.217.134.179/sync_start_all').json()
    update.message.reply_text(msg)


def stop_sync_all(update, context):
    """Send a message when the command /start_sync is issued."""

    msg = requests.get('http://95.217.134.179/sync_stop_all').json()
    update.message.reply_text(msg)
    time.sleep(30)
    msg = requests.get('http://95.217.134.179/clean_assetchain_folders').json()
    update.message.reply_text(msg)




def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')



if __name__ == '__main__':
    main()