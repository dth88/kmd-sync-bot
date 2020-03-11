#!/usr/bin/env python3

import logging
import requests
import subprocess

from botlib import def_credentials, check_website_status, check_daemon_status

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # TODO: structure {"servicename":"url"} for services
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)


    updater = Updater("971322549:AAHwgjKp-_i4qbimcSAenYpD_I8CI87uClk", use_context=True)
    checking_health = updater.job_queue
    check_each_minute = checking_health.run_repeating(check_services_status_constantly, interval=60, first=0)
    check_each_hour = checking_health.run_repeating(check_services_status_hour, interval=3600, first=0)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start_sync", start_sync))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("checkstatus", check_services_status))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()





# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start_sync(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! I\'m a Komodo QA department Telegram bot.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def check_services_status(update, context):
    """Checking infra status once"""

    infra_status_message = ""

    for k,v in services.items():
        infra_status_message += check_website_status(v, k)

    for k,v in daemons.items():
        infra_status_message += check_daemon_status(v, k)

    update.message.reply_text(infra_status_message)


def check_services_status_constantly(context: CallbackContext):
    """Checking infra constantly"""

    is_down = False
    infra_status_message = ""

    for k,v in services.items():
        infra_status_message += check_website_status(v, k)

    for k,v in daemons.items():
        infra_status_message += check_daemon_status(v, k)
    
    search_result = infra_status_message.find('is down')
    if search_result != -1:
        is_down = True
    if is_down:
        context.bot.send_message(chat_id='@kmdQAnotifications', text=infra_status_message)
    else:
        pass


def check_services_status_hour(context: CallbackContext):
    """Checking infra status"""
    is_down = False
    infra_status_message = ""

    for k,v in services.items():
        infra_status_message += check_website_status(v, k)

    for k,v in daemons.items():
        infra_status_message += check_daemon_status(v, k)
    
    search_result = infra_status_message.find('is down')
    if search_result != -1:
        is_down = True
    context.bot.send_message(chat_id='@kmdQAnotifications', text=infra_status_message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)





if __name__ == '__main__':
    main()