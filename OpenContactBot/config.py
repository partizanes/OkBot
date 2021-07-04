# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os,configparser

from util import Util

TELEGRAM_CONFIG = Util.getDataFrom('../conf/telegram.json')
HELPDESK_CONFIG = Util.getDataFrom('../conf/helpdesk.json')
MYSQL_CONFIG = Util.getDataFrom('../conf/mysql.json')
SECURITY_CONFIG = Util.getDataFrom('../conf/security.json')
DOMAIN_CONFIG = Util.getDataFrom('../conf/domain.json')
DOMAIN_NEW_CONFIG = Util.getDataFrom('../conf/domainbyapi.json')
ACCAPI_CONFIG = Util.getDataFrom('../conf/accapi.json')
MAIL_CONFIG = Util.getDataFrom('../conf/mail.json')


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
    ########### MYSQL ##############

    @staticmethod
    def getNameHost():
        return MYSQL_CONFIG["host"]

    @staticmethod
    def getMysqlUser():
        return MYSQL_CONFIG["user"]

    @staticmethod
    def getMysqlPass():
        return MYSQL_CONFIG["password"]

    @staticmethod
    def getDbName():
        return MYSQL_CONFIG["db"]

    @staticmethod
    def getDbCharset():
        return MYSQL_CONFIG["charset"]

    ##############################
    ########### SECURITY #########

    @staticmethod
    def getPrivatekey():
        return SECURITY_CONFIG["key"]

    ##############################
    ########### DOMAIN ###########

    @staticmethod
    def getDomainUsername():
        return DOMAIN_CONFIG["user"]

    @staticmethod
    def getDomainPassword():
        return DOMAIN_CONFIG["password"]

    ##############################
    ########### DOMAINNEW ########

    @staticmethod
    def getApiUrl():
        return DOMAIN_NEW_CONFIG["apiUrl"]

    @staticmethod
    def getApiKey():
        return DOMAIN_NEW_CONFIG["apiKey"]

    ##############################
    ########### ACCAPI ###########

    @staticmethod
    def getAccApiHost():
        return ACCAPI_CONFIG["host"]

    @staticmethod
    def getAccApiToken():
        return ACCAPI_CONFIG["token"]
    ##############################

    ########### MAIL #############

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
