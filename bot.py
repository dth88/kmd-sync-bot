#!/usr/bin/env python3
import logging
import requests
import time
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


api_calls_keyboard = [['Setup binary', 'Server info'],
                      ['Start all', 'Stop all', 'Get status'],
                      ['Pick another server']]
api_calls_markup = ReplyKeyboardMarkup(api_calls_keyboard, one_time_keyboard=True)


def main():
    bot_persistence = DictPersistence()
    updater = Updater("971322549:AAHwgjKp-_i4qbimcSAenYpD_I8CI87uClk", persistence=bot_persistence, use_context=True)
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
                                   MessageHandler(Filters.regex('^(Server info)$'), help),
                                   MessageHandler(Filters.regex('^(Start all)$'), start_sync_all),
                                   CommandHandler('start_sync', start_sync),
                                   MessageHandler(Filters.regex('^(Stop all)$'), stop_sync_all),
                                   CommandHandler('stop_sync', stop_sync),
                                   MessageHandler(Filters.regex('^(Get status)$'), get_current_sync_status),
                                   MessageHandler(Filters.regex('^(Pick another server)$'), help)],

            TYPING_API_CALL: [MessageHandler(Filters.text, received_api_call)],
        },

        fallbacks=[MessageHandler(Filters.regex('^fallback$'), help),
                   CommandHandler('start', start)]
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




def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


@send_typing_action
def start(update, context):
    update.message.reply_text('Hi! Lets configure a new sync server! Please provide data in the following format: server_name,ip,rootpass', reply_markup=configure_markup)
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

    update.message.reply_text("Neat! Now press Done to start the setup.")


    return CONFIGURE

#TYPING_CHOICE
@send_typing_action
def received_server_choice(update, context):
    available_servers = context.user_data['servers']
    for server in available_servers:
        if update.message.text in server['name']:
            context.user_data['choice'] = server
            update.message.reply_text('Now you are in the api state, here you should setup a binary first.')
            return ISSUING_API_COMMANDS


    for server in available_servers:
        if update.message.text not in server['name']:
            update.message.reply_text('Something might be wrong, are you sure you typed the name of the server correctly? try again')
            return CHOOSING_SERVER



#TYPING_API_CALL
def received_api_call(update, context):

    return ISSUING_API_COMMANDS


@send_typing_action
def configure(update, context):
    new_server = context.user_data['new_server']
    ip = new_server['ip']
    rootpass = new_server['pass']

    update.message.reply_text("Starting server setup, could take few minutes...")
    command = "wget https://raw.githubusercontent.com/dathbezumniy/kmd-sync-api/master/sync_api_setup.sh " \
              "&& chmod u+x sync_api_setup.sh && ./sync_api_setup.sh"
    client = SSHClient(ip, user='root', password=rootpass)
    output = client.run_command(command, sudo=True)

    time.sleep(90)

    r = requests.get('http://{}'.format(ip)).json()

    #first setup and if success then add to the persistent var 'servers'
    if "Hi" in r['message']:
        update.message.reply_text("Seems like setup is done.")
        context.user_data['servers'].append(new_server)
        return CHOOSING_SERVER
    else:
        update.message.reply_text("Something might be wrong. API didn't start, try to start over with /start")
        return CONFIGURE
    

@send_typing_action
def make_a_choice(update, context):
    available_servers = context.user_data['servers']
    number_of_servers = len(available_servers)
    if number_of_servers == 1:
        update.message.reply_text('Currently you registered only one server. I\'m gonna pick it for you. Now you are in the api state, here you should setup a binary first.')
        context.user_data['choice'] = available_servers[0]
        return ISSUING_API_COMMANDS

    elif number_of_servers > 1:
        update.message.reply_text('To pick a server just reply with a name. Currently you registered {} servers. Here they are:'.format(number_of_servers))
        msg = ''
        for server in available_servers:
            msg += '{} --> {}'.format(server['name'], server['ip'])
        update.message.reply_text(msg)
        return TYPING_CHOICE


    update.message.reply_text('Something probably went wrong on the configuration stage, you have no registered servers. try to start over with /start')
    return CONFIGURE
    







@send_typing_action
def setup_binary(update, context):
    """Send a message when the command /start_sync is issued."""
    link = {'link' : context.args[0]}
    msg = requests.post('http://{}/upload_binary'.format(), data=link).json()
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return TYPING_API_CALL




@send_typing_action
def get_current_sync_status(update, context):
    msg = requests.get('http://{}/sync_stats_all'.format(context.user_data['choice']['ip'])).json()
    amount = int(msg['amount'])
    stats = msg['stats']
    reply = 'Currently {} assetchains are syncing\n'.format(amount)
    if amount:
        for k,v in stats.items():
            reply += '{}- sync: {}. Blocks {} out of {}\n'.format(v['coin'], v['synced'], v['blocks'], v['longestchain'])
    
    update.message.reply_text(reply, reply_markup=api_calls_markup)


    return TYPING_API_CALL


@send_typing_action
def start_sync(update, context):
    """Send a message when the command /start_sync is issued."""
    for ticker in context.args:
        msg = requests.get('http://{}/sync_start/{}'.format(context.user_data['choice']['ip'], ticker)).json()
        update.message.reply_text(msg, reply_markup=api_calls_markup)

    return TYPING_API_CALL


@send_typing_action
def stop_sync(update, context):
    """Send a message when the command /start_sync is issued."""

    for ticker in context.args:
        msg = requests.get('http://{}/sync_stop/{}'.format(context.user_data['choice']['ip'], ticker)).json()
        update.message.reply_text(msg, reply_markup=api_calls_markup)

    return TYPING_API_CALL


@send_typing_action
def start_sync_all(update, context):
    """Send a message when the command /start_sync is issued."""

    msg = requests.get('http://{}/sync_start_all'.format(context.user_data['choice']['ip'])).json()
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return TYPING_API_CALL


@send_typing_action
def stop_sync_all(update, context):
    """Send a message when the command /start_sync is issued."""

    msg = requests.get('http://{}/sync_stop_all'.format(context.user_data['choice']['ip'])).json()
    update.message.reply_text(msg)
    update.message.reply_text('waiting 30 seconds for cleanup of assetchain folders')
    time.sleep(30)
    msg = requests.get('http://{}/clean_assetchain_folders'.format(context.user_data['choice']['ip'])).json()
    update.message.reply_text(msg, reply_markup=api_calls_markup)

    return TYPING_API_CALL


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