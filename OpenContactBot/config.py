# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os,configparser

from util import Util

TELEGRAM_CONFIG = Util.getDataFrom('../conf/telegram.json')
MAIL_CONFIG = Util.getDataFrom('../conf/mail.json')
HELPDESK_CONFIG = Util.getDataFrom('../conf/helpdesk.json')

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
    def getPrivatekey():
        return Config.getConfigValue('security', 'privateKey')

    @staticmethod
    def getDomainUsername():
        return Config.getConfigValue('domain', 'username')

    @staticmethod
    def getDomainPassword():
        return Config.getConfigValue('domain', 'password')

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



    ########### HELPDESK ###########

    @staticmethod
    def getHdBotToken():
        return HELPDESK_CONFIG["token"]

    @staticmethod
    def getHdUrl():
        return HELPDESK_CONFIG["url"]

    @staticmethod
    def getHdBotUsername():
        return HELPDESK_CONFIG["username"]

    @staticmethod
    def getHdBotPassword():
        return HELPDESK_CONFIG["password"]
        
    @staticmethod
    def getHdSession():
        return HELPDESK_CONFIG["session"]

    ################################



    ########### MAIL ###########

    @staticmethod
    def getSmtpServer():
        return MAIL_CONFIG["server"]
    
    @staticmethod
    def getMailFrom():
        return MAIL_CONFIG["from"]

    @staticmethod
    def getDnsAdmin():
        return MAIL_CONFIG["dmsadmin"]

    ############################
