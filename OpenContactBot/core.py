# -*- coding: utf-8 -*-
# by Part!zanes 2017

import time
import threading
from log import Log
from config import Config
from openbot import OpenBot
from checkHandler import CheckHandler
from accountloader import cronReloadListAccounts
from domainapi import DomainApi
from cpanelServerHandler import cpanelServerHandler

coreLog = Log('Core')
coreLog.info('Core started.')

dApi = DomainApi()
checkhandler = CheckHandler()
openbot = OpenBot(Config.getToken())
cServHandler = cpanelServerHandler()


t = threading.Thread(target=openbot.listening, args=(dApi,))
t.daemon = True
t.start()

t2 = threading.Thread(target=checkhandler.start, args=(openbot,))
t2.daemon = True
t2.start()

t3 = threading.Thread(target=cronReloadListAccounts)
t3.daemon = True
t3.start()

t4 = threading.Thread(target=dApi.startDomainCheck, args=(openbot,))
t4.daemon = True
t4.start()

t5 = threading.Thread(target=cServHandler.start, args=(openbot,))
t5.daemon = True
t5.start()

while 1:
    time.sleep(30)
    #coreLog.info('tick.')

