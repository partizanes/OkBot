# -*- coding: utf-8 -*-
# by Part!zanes 2019


from cpanelapi import client
from util import Util


def loadServerList():
    cpanelApiClient = {}
    data = Util.getDataFrom('../conf/cpanel.json')

    for key, value in data['cpanel'].items():
            cpanelApiClient[key] = client.Client('root', key, access_hash=value)

    return cpanelApiClient

cpanelApiClient = loadServerList()
