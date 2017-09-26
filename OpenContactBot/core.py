# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os, time, git
import threading
from log import Log
from util import Util
from config import Config
from openbot import OpenBot
from domainapi import DomainApi
from checkHandler import CheckHandler
from accountloader import cronReloadListAccounts
from cpanelServerHandler import cpanelServerHandler

coreLog = Log('Core')
coreLog.info('Core started.')

dApi = DomainApi()
checkhandler = CheckHandler()
openbot = OpenBot(Config.getToken())
cServHandler = cpanelServerHandler()

if(Util.needUpdate()):
    os.chdir('..')
    g = git.cmd.Git(os.getcwd())
    updateLog = g.pull()
    coreLog.warning(updateLog)
    openbot.sendMessageGroup(updateLog)
    os.chdir('OpenContactBot')

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

