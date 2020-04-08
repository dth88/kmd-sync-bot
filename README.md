# Komodo telegram sync-bot utility

## TL;DR

This bot will help you to manage multiple sync servers with custom binaries. Just type /start and it will guide you through the setup process.






...... waiting for delivery of some juicy GIFS







## Pre-phase
This bot and complementary sync api are in the very early development stage, so the security of the whole thing is still a big question and if you notice any bugs or issues please let me know here via issues or im usually available at komodo discord channel @dth. If you need any guidance on how to add features/configure or you want to propose an improvement please do not hesitate as well. For now there's no database or serialization of any kind, so as soon as your bot reboots/restarts/crashes you will loose all your configured servers, but if you are going to setup the server that already has an api installed and running the configuration function will recognize that via simple request call to root endpoint and wont make you wait.

For now both bot and api tested only on: Ubuntu 18.04 LTS bionic

## Installation
I've configured both sync-bot(this repo) and sync-api(https://github.com/dathbezumniy/kmd-sync-api) to work with supervisor so basically you just need to do the following:

```sh    assuming you are in (~)root directory

git clone https://github.com/dathbezumniy/kmd-sync-bot.git

cd kmd-sync-bot

pip3 install -r requirements.txt

export SYNC_BOT_TOKEN='your telegram token here'

supervisord -c /root/kmd-sync-bot/supervisord.conf

```

## Possible manual routine:
```sh
ps aux | grep python``` - checks if supervisor and sync-bot are running.
If by any chance you do not see something like that in the output:
        /usr/bin/python3 /usr/local/bin/supervisord -c /root/kmd-sync-bot/supervisord.conf
        /usr/bin/python3 /root/kmd-sync-bot/bot.py

Then you should check bot error log:
```sh
cat logs/sync-bot.err.log
```



If you cant figure the problem out, do not hesitate to paste this error message to me @dth at discord komodo channel or simply open up an issue here. If you have ideas on what should be done to make this bot even better, let me know.



## Using the bot

Commands that are accessible throughout all states:
/start - sets up a new server.
/help - prints this message.

For the purpose of better UX we decided to go with a conversational bot with 3 main states and quite a few buttons:

### CONFIGURE_STATE
This state is triggered when you issue /start command, it lets you setup a new server. /start and /help cmd's are always available to you in any state.
Available buttons:   Done - to start the configuration with provided server data.


### CHOOSE_SERVER_STATE
This is the state where you can switch between different servers that you have setup.
Available buttons:   Pick a server - to list available servers.


### API_COMMANDS_STATE
This is the state where you can start/stop tickers or get a current sync status on the server.
Available keyboard:  Stop all - Stops all subchains from launch_params.py with optional cleanup.
                     Stop KMD - Stops main chain individually with optional cleanup.
                    Start all - Starts all subchains from launch_params.py
                    Start KMD - Starts main chain individually.
                   Get status - Displays a table with chains that are currently syncing.
                  Restart API - Triggers automatically when you upload new launch_params.py in chat.             
                  Server info - Displays current server info.
                Change server - Sends you to CHOOSE_SERVER_STATE to pick another server.
                Launch params - Drops current launch_params.py file in chat. Edit it and drop it back.
            Available tickers - Displays all tickers that currently available.
                  
Other than the keyboard commands there are few others:
/start_sync AXO BET PANGEA - start tickers individually.
 /stop_sync AXO BET PANGEA - stop tickers individually with optional cleanup.


