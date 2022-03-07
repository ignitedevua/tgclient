#! /usr/bin/env python3
# -*- coding: utf-8 -*-

### DOCS
#  https://docs.telethon.dev/en/stable/basic/updates.html

import re
import os
import json
import sys
import time
import asyncio
import configparser

from enum import unique
from telethon import TelegramClient, events

from urllib.parse import urlparse
from urllib.parse import urlunsplit

import CountryIp

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

config = configparser.ConfigParser()
config.read("config.ini")

# Read config
api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

URL_REGEX = r"""\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"""

from telethon.sync import TelegramClient, events
from telethon import TelegramClient, events

client = TelegramClient(username, api_id, api_hash)

SAVED_URLS = []
PAGES_JSON_FILENAME = "pages.json"

FILTER_ZONE = {"ru", "by"}

GIT_PUSH_TIME = time.time()

def gitPush():
    global GIT_PUSH_TIME
    now = time.time()
    if now > GIT_PUSH_TIME + 60*60:
        # git add f'{PAGES_JSON_FILENAME}'
        # git comit -m "update f'{PAGES_JSON_FILENAME}'"
        # git push
        GIT_PUSH_TIME = now



def loadPages():
    global SAVED_URLS
    with open(PAGES_JSON_FILENAME,"rb") as json_file:
        tmp = json.load(json_file)
        SAVED_URLS = [
                        item["page"]
                        for item in tmp
                    ]


def saveFile(raw_list):
    list_set = set(raw_list)
    unique_list = list(list_set)
    formatted = [ {"page":unique_list[i]}for i in range(0, len(unique_list))  ]
    if len(formatted)!=0:
        jsonString = json.dumps(formatted)
        jsonFile = open(PAGES_JSON_FILENAME, "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        gitPush()


def normalizeUrl(url):
    _url = url
    if not _url.startswith('http'):
        _url = 'http://' + _url
    p = urlparse(_url, 'http')
    scheme = p.scheme
    port = p.port
    if port == 443:
        scheme = "https"
    return f"{scheme}://{p.hostname}{f':{p.port}' if p.port else '' }"



def validateUrl(url):
    if url:
        domain = normalizeUrl(url)
        if domain and domain.split('.')[-1] in FILTER_ZONE:
            print(f' + {domain}')
            return domain
        else:
            zone = CountryIp.getCountryByUrl(domain)
            if zone and zone.lower() in FILTER_ZONE:
                print(f' + {domain}')
                return domain

        print(f' - {domain}')
    return None
    

def updateJSON(urllist):
    if len(urllist) > 0:    
        for url in urllist:
            validated = validateUrl(url)
            if validated != None:
                SAVED_URLS.append(validated)
        saveFile(SAVED_URLS)


@client.on(events.NewMessage)
async def oneventsNewMessage(event):
    matches = re.findall(URL_REGEX,event.raw_text)
    # print(event.raw_text)
    # print(matches)
    updateJSON(matches)
    return



loadPages()
client.start()
client.run_until_disconnected()
