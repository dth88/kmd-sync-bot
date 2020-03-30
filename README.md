# Komodo telegram sync bot utility

## TL;DR
......



## Pre-phase
This bot and complementary sync api are in the early development stages, so the security of the whole thing is still a big question and if there are any bugs or issues please let me know, im usually always available at komodo discord channel @dth. Also if you need any guidance on how to add features/configure or you want to propose an improvement please do not hesitate to contact me.
For now there's no database or serialization of any kind, so as soon as your bot reboots/restarts/crashes you will loose all your configured servers, but if you are going to setup the server that already has an api installed and up the configuration function will recognize that and wont make you wait.


## Installation
I've configured both bot and api to work with supervisor so basically you just need to clone repo, install requirements, put you telegram token in SYNC_BOT_TOKEN env var and start it with supervisord.
For now this bot capabilities will help you to manage multiple sync servers with custom binaries, as soon as you launch it and type /start bot will guide you through the setup process.


## Using the bot
I've made this bot a conversational one with 3 different states:

### CONFIGURE_STATE
This state is triggered when you issue /start command and lets you setup a new server. /start and /help cmd's are always available to you in any state.

### CHOOSING_SERVER_STATE
This is the state where you can switch between different servers that you have setup.

### ISSUING_API_COMMANDS_STATE
This is the state where you can start/stop tickers or get a current sync status on the server.

