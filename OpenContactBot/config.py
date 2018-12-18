# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os,configparser

from util import Util

TELEGRAM_CONFIG = Util.getDataFrom('../conf/telegram.json')

class Config(object):

    configParser = configparser.RawConfigParser()
    configFilePath = (os.path.join(os.getcwd(),'config.cfg'))

    @classmethod
    def initializeConfig(cls):
        cls.configParser.read(cls.configFilePath)

    @classmethod
    def saveConfig(cls):
        with open(cls.configFilePath, 'w') as configfile:
            cls.configParser.write(configfile)
        

    @classmethod
    def getConfigValue(cls, group, key):
        return cls.configParser.get(group, key)
    
    @classmethod
    def setConfigValue(cls, group, key, value):
         cls.configParser.set(group, key, value)

    @staticmethod
    def getNameHost():
        return Config.getConfigValue('helpDeskMysql','host')

    @staticmethod
    def getDbName():
        return Config.getConfigValue('helpDeskMysql','db')

    @staticmethod
    def getDbCharset():
        return Config.getConfigValue('helpDeskMysql','charset')

    @staticmethod
    def getMysqlUser():
        return Config.getConfigValue('helpDeskMysql','user')

    @staticmethod
    def getMysqlPass():
        return Config.getConfigValue('helpDeskMysql', 'password')
  
    @staticmethod
    def getCpanelToken(value):
        return Config.getConfigValue('cpanel', value)

    @staticmethod
    def getPrivateId():
        return Config.getConfigValue('security', 'privateId')

    @staticmethod
    def getPrivatekey():
        return Config.getConfigValue('security', 'privateKey')

    @staticmethod
    def getDomainUsername():
        return Config.getConfigValue('domain', 'username')

    @staticmethod
    def getDomainPassword():
        return Config.getConfigValue('domain', 'password')

    @staticmethod
    def getHdBotToken():
        return Config.getConfigValue('hd', 'token')

    @staticmethod
    def getHdBotUsername():
        return Config.getConfigValue('hd', 'username')

    @staticmethod
    def getHdBotPassword():
        return Config.getConfigValue('hd', 'password')

    @staticmethod
    def getHdUrl():
        return Config.getConfigValue('hd', 'url')
        
    @staticmethod
    def getHdSession():
        return Config.getConfigValue('hd', 'session')
    
    @staticmethod
    def getSmtpServer():
        return Config.getConfigValue('mail', 'server')
    
    @staticmethod
    def getMailFrom():
        return Config.getConfigValue('mail', 'from')

    @staticmethod
    def getDnsAdmin():
        return Config.getConfigValue('mail', 'dmsadmin')

    @staticmethod
    def getExcludeDomainList():
        exclude_list = []

        for item in Config.getConfigValue('exclude', 'create').replace(' ', '').split(','):
            exclude_list.append(item)

        exclude_list = list(filter(None, exclude_list))
        return exclude_list


    ########### TELEGRAM ###########

    @staticmethod
    def getToken():
        return TELEGRAM_CONFIG["token"]

    @staticmethod
    def getPrivatesId():
        return TELEGRAM_CONFIG["privatesId"]

    @staticmethod
    def getGroupId():
        return TELEGRAM_CONFIG["groupid"]

    @staticmethod
    def getAdminList():
        admlist = TELEGRAM_CONFIG["admlist"]

        return {int(id):admlist[id] for id in admlist}

    ################################


