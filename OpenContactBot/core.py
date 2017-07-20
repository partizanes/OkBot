# -*- coding: utf-8 -*-
# by Part!zanes 2017

import time
import threading
from log import Log
from config import Config
from openbot import OpenBot
from checkHandler import CheckHandler

coreLog = Log('Core')
coreLog.info('Core started.')

openbot = OpenBot(Config.getToken())
t = threading.Thread(target=openbot.listening)
t.daemon = True
t.start()

checkhandler = CheckHandler()
t2 = threading.Thread(target=checkhandler.start(openbot))
t2.daemon = True
t2.start()


while 1:
    time.sleep(10)
    coreLog.info('tick.')
    #openbot.sendMessage('233355404', 'test')
    #bot.okbot.sendMessage('-201136336', 'test')