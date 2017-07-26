# -*- coding: utf-8 -*-
# by Part!zanes 2017

import time
import threading
from log import Log
from config import Config
from openbot import openbot
from checkHandler import CheckHandler
from accountloader import cronReloadListAccounts


coreLog = Log('Core')
coreLog.info('Core started.')

t = threading.Thread(target=openbot.listening)
t.daemon = True
t.start()

checkhandler = CheckHandler()
t2 = threading.Thread(target=checkhandler.start)
t2.daemon = True
t2.start()

t3 = threading.Thread(target=cronReloadListAccounts)
t3.daemon = True
t3.start()


while 1:
    time.sleep(10)
    coreLog.info('tick.')

    #openbot.sendMessage('233355404', 'test')
    #bot.okbot.sendMessage('-201136336', 'test')