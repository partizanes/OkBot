# -*- coding: utf-8 -*-
# by Part!zanes 2017

from crypto import Crypto
from cpanelapi import client
from config import Config

def loadServerList():
    cpanelApiClient = {}

    #Remove it after deploy
    Config.initializeConfig()

    cpanelApiClient['s4.open.by'] = client.Client('root', 's4.open.by', access_hash=Crypto.getCpanelToken('s4token'))
    cpanelApiClient['s5.open.by'] = client.Client('root', 's5.open.by', access_hash=Crypto.getCpanelToken('s5token'))
    cpanelApiClient['s6.open.by'] = client.Client('root', 's6.open.by', access_hash=Crypto.getCpanelToken('s6token'))
    cpanelApiClient['s7.open.by'] = client.Client('root', 's7.open.by', access_hash=Crypto.getCpanelToken('s7token'))
    cpanelApiClient['s8.open.by'] = client.Client('root', 's8.open.by', access_hash=Crypto.getCpanelToken('s8token'))
    cpanelApiClient['s9.open.by'] = client.Client('root', 's9.open.by', access_hash=Crypto.getCpanelToken('s9token'))

    return cpanelApiClient

cpanelApiClient = loadServerList()
