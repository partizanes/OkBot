# -*- coding: utf-8 -*-
# by Part!zanes 2017

import logging
from datetime import datetime
from colorama import init, Fore

init()

class Log(object):
    def __init__(self, Module=None):
        self.Module = Module
        logging.basicConfig(format = u'[%(asctime)s][%(levelname)s][' + self.Module + '] %(message)s', level = logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', filename = u'bot.log')

    def debug(self, message):
        logging.debug( u'%s'%(message))
        print(Fore.WHITE + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'DEBUG', message))

    def info(self, message):
        logging.info( u'%s'%(message))
        print(Fore.GREEN + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'INFO', message))

    def warning(self, message):
        logging.warning( u'%s'%(message))
        print(Fore.LIGHTYELLOW_EX +  u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'WARN', message))


    def error(self, message):
        logging.error( u'%s'%(message))
        print(Fore.RED + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'ERROR', message))

    def critical(self, message):
        logging.error( u'%s'%(message))   
        print(Fore.LIGHTRED_EX + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'CRITICAL', message))
