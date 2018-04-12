# -*- coding: utf-8 -*-
# by Part!zanes 2017

from crypto import Crypto
from cpanelapi import client
from config import Config

def loadServerList():
    cpanelApiClient = {}

    #Remove it after deploy
    Config.initializeConfig()

    cpanelApiClient['s2.open.by'] = client.Client('root', 's2.open.by', password=Crypto.getCpanelPass())
    cpanelApiClient['s3.open.by'] = client.Client('root', 's3.open.by', password=Crypto.getCpanelPass())
    cpanelApiClient['s4.open.by'] = client.Client('root', 's4.open.by', access_hash=Crypto.getCpanelToken('s4token'))
    cpanelApiClient['s5.open.by'] = client.Client('root', 's5.open.by', access_hash=Crypto.getCpanelToken('s5token'))
    cpanelApiClient['s6.open.by'] = client.Client('root', 's6.open.by', access_hash=Crypto.getCpanelToken('s6token'))
    cpanelApiClient['s7.open.by'] = client.Client('root', 's7.open.by', access_hash=Crypto.getCpanelToken('s7token'))
    cpanelApiClient['s8.open.by'] = client.Client('root', 's7.open.by', access_hash=Crypto.getCpanelToken('s7token'))

    return cpanelApiClient

cpanelApiClient = loadServerList()
