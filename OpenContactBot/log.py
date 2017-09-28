# -*- coding: utf-8 -*-
# by Part!zanes 2017

import logging
from datetime import datetime
from colorama import init, Fore

init()

class Log(object):
    def __init__(self, Module=None):
        try:
            self.Module = Module
            logging.basicConfig(format = u'[%(asctime)s][%(levelname)s][' + self.Module + '] %(message)s', level = logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', filename = u'bot.log')
        except UnicodeEncodeError:
            pass

    def debug(self, message):
        try:
            logging.debug( u'%s'%(message))
            print(Fore.WHITE + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'DEBUG', message))
        except UnicodeEncodeError:
            pass

    def info(self, message):
        try:
            logging.info( u'%s'%(message))
            print(Fore.GREEN + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'INFO', message))
        except UnicodeEncodeError:
            pass

    def warning(self, message):
        try:
            logging.warning( u'%s'%(message))
            print(Fore.LIGHTYELLOW_EX +  u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'WARN', message))
        except UnicodeEncodeError:
            pass

    def error(self, message):
        try:
            logging.error( u'%s'%(message))
            print(Fore.RED + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'ERROR', message))
        except UnicodeEncodeError:
            pass

    def critical(self, message):
        try:
            logging.error( u'%s'%(message))
            print(Fore.LIGHTRED_EX + u'[%s][%s][%s] %s'%(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), self.Module, 'CRITICAL', message))
        except UnicodeEncodeError:
            pass 
