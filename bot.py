#!/usr/bin/env python3
import logging
import requests
import time
import os
from emoji import emojize
from pssh.clients import SSHClient
from functools import wraps
from telegram import ReplyKeyboardMarkup, ChatAction
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, DictPersistence)



#states
CONFIGURE, CHOOSING_SERVER, ISSUING_API_COMMANDS, TYPING_REPLY, TYPING_CHOICE, TYPING_API_CALL = range(6)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

configure_keyboard = [['Done']]
configure_markup = ReplyKeyboardMarkup(configure_keyboard, one_time_keyboard=True)


choose_server_keyboard = [['Pick a server']]
choose_server_markup = ReplyKeyboardMarkup(choose_server_keyboard, one_time_keyboard=True)

api_calls_keyboard = [['Start all', 'Stop all', 'Get status'],
                      ['Pick another server', 'Server info']]
api_calls_markup = ReplyKeyboardMarkup(api_calls_keyboard, one_time_keyboard=True)


def main():
    bot_persistence = DictPersistence()
    updater = Updater(os.environ['SYNC_BOT_TOKEN'], persistence=bot_persistence, use_context=True)
    dp = updater.dispatcher


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={

            CONFIGURE: [MessageHandler(Filters.regex('^(Done)$'), configure)],

            TYPING_REPLY: [MessageHandler(Filters.text, received_config_information)],

            CHOOSING_SERVER: [MessageHandler(Filters.regex('^(Pick a server)$'), make_a_choice)],
            
            TYPING_CHOICE: [MessageHandler(Filters.text, received_server_choice)],

            ISSUING_API_COMMANDS: [MessageHandler(Filters.regex('^(Setup binary)$'), setup_binary),
                                   CommandHandler('setup_binary', setup_binary),
                                   MessageHandler(Filters.regex('^(Server info)$'), show_current_server),
                                   MessageHandler(Filters.regex('^(Start all)$'), start_sync_all),
                                   CommandHandler('start_sync', start_sync),
                                   MessageHandler(Filters.regex('^(Stop all)$'), stop_sync_all),
                                   CommandHandler('stop_sync', stop_sync),
                                   MessageHandler(Filters.regex('^(Get status)$'), get_current_sync_status),
                                   MessageHandler(Filters.regex('^(Pick another server)$'), make_a_choice)],

            TYPING_API_CALL: [MessageHandler(Filters.text, received_api_call)],
        },

        fallbacks=[MessageHandler(Filters.regex('^fallback$'), help),
                   CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)
    
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


@send_typing_action
def start(update, context):
    update.message.reply_text('Hi! Lets configure a new komodo sync server! Please provide data in the \nfollowing format: server_name,ip,rootpass')
    try:
        if context.user_data['servers']:
            pass
    except KeyError:
        context.user_data['servers'] = []
    context.user_data['new_server'] = {}

    return TYPING_REPLY


#TYPING_REPLY
def received_config_information(update, context):
    name, ip, rootpass = update.message.text.split(",")
    context.user_data['new_server'] = {'name' : name, 'ip' : ip, 'pass' : rootpass}

    update.message.reply_text("Neat! Now press Done to start the setup.", reply_markup=configure_markup)


    return CONFIGURE


#TYPING_CHOICE
@send_typing_action
def received_server_choice(update, context):
    available_servers = context.user_data['servers']
    for server in available_servers:
        if update.message.text in server['name']:
            context.user_data['current_server'] = server
            update.message.reply_text('Now you are in the api state, here you should setup a binary first. \nUse: /setup_binary [link_to_a_downloadable_binaries_in.zip]', reply_markup=api_calls_markup)
            return ISSUING_API_COMMANDS


    update.message.reply_text('Something might be wrong, are you sure you typed the name of the server correctly? try again', reply_markup=choose_server_markup)
    return CHOOSING_SERVER


#TYPING_API_CALL
def received_api_call(update, context):

    return ISSUING_API_COMMANDS



# TODO: end-to-end test to check if the daemon is able to start.
@send_typing_action
def configure(update, context):
    new_server = context.user_data['new_server']
    ip = new_server['ip']
    rootpass = new_server['pass']

    r = requests.get('http://{}'.format(ip)).json()
    if "Hi" in r['message']:
        update.message.reply_text("Seems like setup is already done on this server. Now you should pick a server.", reply_markup=choose_server_markup)
        context.user_data['servers'].append(new_server)
        return CHOOSING_SERVER

    update.message.reply_text("Starting server setup, could take a few minutes...")
    command = "wget https://raw.githubusercontent.com/dathbezumniy/kmd-sync-api/master/sync_api_setup.sh " \
              "&& chmod u+x sync_api_setup.sh && ./sync_api_setup.sh"
    client = SSHClient(ip, user='root', password=rootpass)
    output = client.run_command(command, sudo=True)

    time.sleep(200)

    r = requests.get('http://{}'.format(ip)).json()
    if "Hi" in r['message']:
        update.message.reply_text("Seems like setup is done. Now you should pick a server.", reply_markup=choose_server_markup)
        context.user_data['servers'].append(new_server)
        return CHOOSING_SERVER
    
    
    update.message.reply_text("Something might be wrong. API didn't start, try to start over the configuration with /start")
    return CONFIGURE


@send_typing_action
def make_a_choice(update, context):
    available_servers = context.user_data['servers']
    number_of_servers = len(available_servers)
    if number_of_servers == 1:
        update.message.reply_text('Currently you have registered only one server. I\'m gonna pick it for you. \nNow you are in the API state, here you should setup a binary first.\n Use /setup_binary [link-to-a-downloadable-binaries-in.zip]', reply_markup=api_calls_markup)
        context.user_data['current_server'] = available_servers[0]
        return ISSUING_API_COMMANDS

    elif number_of_servers > 1:
        update.message.reply_text('To pick a server just reply with a name. Currently you registered {} servers. Here they are:'.format(number_of_servers))
        msg = ''
        for server in available_servers:
            msg += '{} --> {}\n'.format(server['name'], server['ip'])
        update.message.reply_text(msg)
        return TYPING_CHOICE


    update.message.reply_text('Something probably went wrong on the configuration stage, you have no registered servers. try to start over with /start')
    return CONFIGURE
    




#### API CALLS


@send_typing_action
def setup_binary(update, context):
    link = {'link' : context.args[0]}
    msg = requests.post('http://{}/upload_binary'.format(context.user_data['current_server']['ip']), data=link).json()
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return ISSUING_API_COMMANDS


@send_typing_action
def get_current_sync_status(update, context):
    msg = requests.get('http://{}/sync_stats_all'.format(context.user_data['current_server']['ip'])).json()
    amount = int(msg['amount'])
    stats = msg['stats']
    reply = 'Currently {} assetchains are syncing:\n'.format(amount)
    reply += '{:10}|  {:9}|  {:9}|  {:9}|  {:9}\n'.format('Ticker', 'Sync', 'Got', 'Total', 'Sync%')
    
    width = 9
    if amount:
        for k,v in stats.items():
            if v['synced']:
                reply += '{:{width}}{:{width}}{:{width}}{:{width}}{:{width}.0%}\n'.format(v['coin'], 
                                                            emojize(":white_check_mark:", use_aliases=True),
                                                            v['blocks'],
                                                            v['longestchain'],
                                                            zero_division_fix(int(v['blocks']), int(v['longestchain']),
                                                            width=width))
            else:
                reply += '{:{width}}{:{width}}{:{width}}{:{width}}{:{width}.0%}\n'.format(v['coin'],
                                                            emojize(":no_entry:", use_aliases=True),
                                                            v['blocks'],
                                                            v['longestchain'],
                                                            zero_division_fix(int(v['blocks']), int(v['longestchain'])
                                                            width=width))
            
    
    update.message.reply_text(reply, reply_markup=api_calls_markup)


    return ISSUING_API_COMMANDS



def zero_division_fix(blocks, longestchain):
    return blocks / longestchain if longestchain else 0



@send_typing_action
def start_sync(update, context):
    for ticker in context.args:
        msg = requests.get('http://{}/sync_start/{}'.format(context.user_data['current_server']['ip'], ticker)).json()
        update.message.reply_text(msg, reply_markup=api_calls_markup)

    return ISSUING_API_COMMANDS


@send_typing_action
def stop_sync(update, context):
    for ticker in context.args:
        msg = requests.get('http://{}/sync_stop/{}'.format(context.user_data['current_server']['ip'], ticker)).json()
        update.message.reply_text(msg, reply_markup=api_calls_markup)

    return ISSUING_API_COMMANDS


@send_typing_action
def start_sync_all(update, context):
    msg = requests.get('http://{}/sync_start_all'.format(context.user_data['current_server']['ip'])).json()
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return ISSUING_API_COMMANDS


@send_typing_action
def stop_sync_all(update, context):
    msg = requests.get('http://{}/sync_stop_all'.format(context.user_data['current_server']['ip'])).json()
    update.message.reply_text(msg)
    update.message.reply_text('waiting 30 seconds for cleanup of assetchain folders')
    time.sleep(30)
    msg = requests.get('http://{}/clean_assetchain_folders'.format(context.user_data['current_server']['ip'])).json()
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return ISSUING_API_COMMANDS


@send_typing_action
def show_current_server(update, context):
    current_server = context.user_data['current_server']
    name = current_server['name']
    ip = current_server['ip']
    msg = 'Currently you are on {}, --> {}'.format(name, ip)
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return ISSUING_API_COMMANDS



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


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)











if __name__ == '__main__':
    main()