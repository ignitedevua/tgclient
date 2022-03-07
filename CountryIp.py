#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

import socket    

from urllib.parse import urlparse
from urllib.parse import urlunsplit

def getCountryByUrl(url):
    if not url:
        return None
    
    p = urlparse(url, 'http')
    return getCountryByHost(p.hostname)

def getCountryByHost(host):
    if not host:
        return None
    ip = None
    try:    
        ip = socket.gethostbyname(host)
    except:
        print(f'Unable get host: {host}')
        pass
    return getCountryByIP(ip)


def getCountryByIP(ip):
    if not ip:
        return None
    endpoint = f'https://ipinfo.io/{ip}/json'
    response = requests.get(endpoint, verify = True)

    if response.status_code != 200:
        return None

    data = response.json()
    return data["country"] if "country" in data else None
