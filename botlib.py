import json
import time
import re
import sys
import pickle
import platform
import os
import subprocess
import requests
import signal
from slickrpc import Proxy
from emoji import emojize
from binascii import hexlify
from binascii import unhexlify
from functools import partial
from shutil import copy


def def_credentials(chain):
    rpcport ='';
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)

    return Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


def check_website_status(url, service_name):
    status_line = ""
    try:
        r = requests.get(url)
        if r.status_code == 200:
            status_line = emojize(":white_check_mark: ", use_aliases=True) + service_name + " is up\n"
        else:
            status_line = emojize(":dizzy_face: ", use_aliases=True) + service_name + " is down\n"
    except Exception as e:
        status_line = emojize(":dizzy_face: ", use_aliases=True) + service_name + " is down\n"
    return status_line


def check_daemon_status(ac_name, service_name):
    status_line = ""
    try:
        rpc_proxy = def_credentials(ac_name)
        if rpc_proxy.getinfo()["blocks"] == rpc_proxy.getinfo()["longestchain"]:
            status_line = emojize(":white_check_mark: ", use_aliases=True) + service_name + " is up\n"
        else:
            status_line = emojize(":dizzy_face: ", use_aliases=True) + service_name + " is down\n"
    except Exception as e:
        status_line = emojize(":dizzy_face: ", use_aliases=True) + service_name + " is down\n"
    return status_line