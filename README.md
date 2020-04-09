# Komodo telegram sync-bot utility

## TL;DR

This bot will help you to manage multiple sync servers with custom binaries. Just type /start and it will guide you through the setup process.






...... waiting for delivery of some juicy GIFS







## Pre-phase
This bot and complementary sync api are in the very early development stage, so the security of the whole thing is still a big question and if you notice any bugs or issues please let me know here via issues or at komodo discord channel @dth. If you need any guidance on how to add features/configure or you want to propose an improvement please do not hesitate. For now there's no database or serialization of any kind, so as soon as your bot reboots/restarts/crashes you will loose all your configured servers, but if you are going to setup the server that already has an api installed and running the configuration function will recognize that via simple request call to root endpoint and wont make you wait. Another important remark would be that we have not implemented any foolproofing, so bot may be fragile to inputs and overall sloppy users.

For now both bot and api tested only on: Ubuntu 18.04 LTS bionic

## Installation

If you are on a fresh server then do these preparations:

```sh
sudo apt-get -y update
sudo apt-get -y install python3.6
sudo apt-get -y install python3-pip
sudo apt-get -y install git
pip3 install setuptools
pip3 install wheel
```

I've configured both sync-bot(current-repo) and sync-api(https://github.com/dathbezumniy/kmd-sync-api) to work with supervisor, so basically you just need to do the following:

```sh    

git clone https://github.com/dathbezumniy/kmd-sync-bot.git

cd kmd-sync-bot

pip3 install -r requirements.txt

export SYNC_BOT_TOKEN='your telegram token here'

supervisord -c /root/kmd-sync-bot/supervisord.conf
```

## Manual routine if something goes wrong:
Check if supervisord and sync-bot started properly:
```sh 
ps aux | grep python 
```

If you do not see bot.py running then you should check supervisord or bot error log:

```sh
cat logs/sync-bot.err.log
cat logs/supervisord.log
```

If you fixed the problem then start bot again with:

```sh
supervisorctl start sync-bot
supervisorctl stop sync-bot
supervisorctl restart sync-bot
```

If you cant figure the problem out, do not hesitate to paste this error message to me @dth on discord komodo channel or simply open up an issue here. If you have any ideas on what should be done to make this bot even better, let me know.


## Using the bot

Commands that are accessible throughout all states:
```
/start - sets up a new server.
/help - prints help message.
```

For the purpose of better UX we decided to go with a conversational bot with 3 main states and quite a few buttons:

### CONFIGURE_STATE
This state is triggered when you issue /start, it lets you setup a new server.
```
Available keyboard:   Done - to start the configuration with provided server credentials.
```

### CHOOSE_SERVER_STATE
This is the state where you can switch between different servers that you have previously setup.
```
Available keyboard:   Pick a server - to list available servers.
```

### API_COMMANDS_STATE
Once you enter this state, you will be prompted to /setup_binary [link-to-downloadable-binaries-in.zip] this is because basically the whole idea of the bot is to test custom binaries.&nbsp;
!!!>>> komodod binary should be in the root of .zip archive.
This is the state where you can start/stop tickers or get a current sync status on the server.
```
Available keyboard:  Stop all - Stops all subchains from launch_params.py with optional cleanup.
                     Stop KMD - Stops main chain individually with optional cleanup.
                    Start all - Starts all subchains from launch_params.py
                    Start KMD - Starts main chain individually.
                   Get status - Displays a table with chains that are currently syncing.           
                  Server info - Displays current server info.
                Launch params - Drops current launch_params.py file in chat. Edit it and drop it back.
                Change server - Sends you to CHOOSE_SERVER_STATE to pick different server.
            Available tickers - Displays all tickers that currently available.
                  
Other than the keyboard commands there are few others:
/start_sync AXO BET PANGEA - start tickers individually.
 /stop_sync AXO BET PANGEA -  stop tickers individually with optional cleanup.
 ```