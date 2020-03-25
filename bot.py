#!/usr/bin/env python3
import logging
import requests
import time
from functools import wraps
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, DictPersistence)


#states
CONFIGURE, CHOOSING_SERVER, ISSUING_COMMANDS = range(3)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

configure_keyboard = [['server_name', 'ipaddr'],
                      ['root_pass', 'all_together', 'done']]
reply_markup = ReplyKeyboardMarkup(configure_keyboard, one_time_keyboard=True)


def main():
    bot_persistence = DictPersistence()
    updater = Updater("971322549:AAHwgjKp-_i4qbimcSAenYpD_I8CI87uClk", persistence=bot_persistence, use_context=True)
    dp = updater.dispatcher


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONFIGURE: [MessageHandler(Filters.regex('^(server_name)$'), configure_name),
                        MessageHandler(Filters.regex('^(ipaddr)$'), configure_ip),
                        MessageHandler(Filters.regex('^(root_pass)$'), configure_root_pass),
                        MessageHandler(Filters.regex('^(all_together)$'), configure_all_together),
                        MessageHandler(Filters.regex('^(done)$'), configure)],

            CHOOSING_SERVER: [MessageHandler(Filters.text, make_a_choice)],

            ISSUING_COMMANDS: [MessageHandler(Filters.text, received_information),],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)


    #dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CommandHandler("start_sync", start_sync))
    #dp.add_handler(CommandHandler("start_sync_all", start_sync_all))
    #dp.add_handler(CommandHandler("stop_sync", stop_sync))
    #dp.add_handler(CommandHandler("stop_sync_all", stop_sync_all))
    #dp.add_handler(CommandHandler("setup_binary", setup_binary))
    #dp.add_handler(CommandHandler("get_current_sync_status", get_current_sync_status))
    #dp.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()


@send_typing_action
def start(update, context):
    update.message.reply_text('Hi! Lets configure a new sync server! Just pick an option and provide the data, press done after you finished.',
                              reply_markup=configure_keyboard)
    try:
        if context.user_data['servers']:
            pass
    except KeyError:
        context.user_data['servers'] = []
    context.user_date['new_server'] = {}


    return CONFIGURE


@send_typing_action
def configure_name(update, context):
    update.message.reply_text('Name your new sync-api server:', reply_markup=configure_keyboard)
    context.user_data['new_server']['name'] = update.message.text


    return CONFIGURE


@send_typing_action
def configure_ip(update, context):
    update.message.reply_text('Please provide ip address of the server:', reply_markup=configure_keyboard)
    context.user_data['new_server']['ip'] = update.message.text


    return CONFIGURE


@send_typing_action
def configure_root_pass(update, context):
    update.message.reply_text('Now, root passsword please:', reply_markup=configure_keyboard)
    context.user_data['new_server']['rootpass'] = update.message.text


    return CONFIGURE


@send_typing_action
def configure_all_together(update, context):
    update.message.reply_text('format: name,ip,rootpassword')


    return CONFIGURE


@send_typing_action
def configure(update, context):
    new_server = context.user_data['new_server']
    #first setup and if success then add to the 'servers'
    context.user_data['servers'].append(new_server)
    

    return CHOOSING_SERVER


@send_typing_action
def make_a_choice(update, context):
    available_servers = context.user_data['servers']
    if len(available_servers) > 1:
        pass
    else:
        update.message.reply_text('')


    return ISSUING_COMMANDS


@send_typing_action
def get_current_sync_status(update, context):
    msg = requests.get('http://95.217.134.179/sync_stats_all').json()
    amount = int(msg['amount'])
    stats = msg['stats']
    reply = 'Currently ' + str(amount) + ' assetchains are syncing\n'
    if amount:
        for k,v in stats.items():
            reply += '{}- sync: {}. Blocks {} out of {}\n'.format(v['coin'], v['synced'], v['blocks'], v['longestchain'])
    
    update.message.reply_text(reply)


@send_typing_action
def setup_binary(update, context):
    """Send a message when the command /start_sync is issued."""
    link = {'link' : context.args[0]}
    msg = requests.post('http://{}/upload_binary'.format(), data=link).json()
    update.message.reply_text(msg)


@send_typing_action
def start_sync(update, context):
    """Send a message when the command /start_sync is issued."""
    for ticker in context.args:
        msg = requests.get('http://95.217.134.179/sync_start/{}'.format(ticker)).json()
        update.message.reply_text(msg)


@send_typing_action
def stop_sync(update, context):
    """Send a message when the command /start_sync is issued."""

    for ticker in context.args:
        msg = requests.get('http://95.217.134.179/sync_stop/{}'.format(ticker)).json()
        update.message.reply_text(msg)


@send_typing_action
def start_sync_all(update, context):
    """Send a message when the command /start_sync is issued."""

    msg = requests.get('http://95.217.134.179/sync_start_all').json()
    update.message.reply_text(msg)


@send_typing_action
def stop_sync_all(update, context):
    """Send a message when the command /start_sync is issued."""

    msg = requests.get('http://95.217.134.179/sync_stop_all').json()
    update.message.reply_text(msg)
    update.message.reply_text('waiting 30 seconds for cleanup of assetchain folders')
    time.sleep(30)
    msg = requests.get('http://95.217.134.179/clean_assetchain_folders').json()
    update.message.reply_text(msg)


@send_typing_action
def help(update, context):
    """Send a message when the command /help is issued."""
    help_msg  = 'Configuration:\n'
    help_msg += '/configure - setup a new server.\n'
    help_msg += '/show_available_servers - list available servers.\n'
    help_msg += '/choose_server 1 - select server to execute commands on.\n'
    help_msg += '/setup_binary - upload a new binary to the server.\n'
    help_msg += '           \n'
    help_msg += 'Routine cmds:\n'
    help_msg += '/start_sync_all - start all tickers without KMD.\n'
    help_msg += '/start_sync KMD AXO BET - start tickers individually.\n'
    help_msg += '/stop_sync_all - stop all tickers (will stop them, wait for the processes to close for 30s and then do cleanup of assetchain folders).\n'
    help_msg += '/stop_sync KMD AXO BET - stop tickers individually without cleanup.\n'
    help_msg += '/get_current_sync_status - dump sync progress on all initialized tickers.\n'

    update.message.reply_text(help_msg)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func



if __name__ == '__main__':
    main()