# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os,configparser

class Config(object):

    configParser = configparser.RawConfigParser()
    configFilePath = (os.path.join(os.getcwd(),'config.cfg'))

    @classmethod
    def initializeConfig(cls):
        cls.configParser.read(cls.configFilePath)

    @classmethod
    def getConfigValue(cls, group, key):
        return cls.configParser.get(group, key)

    @staticmethod
    def getToken():
        return Config.getConfigValue('openContactBot','TOKEN')

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
    def getCpanelPass():
        return Config.getConfigValue('cpanel', 'password')

    @staticmethod
    def getCpanelToken(value):
        return Config.getConfigValue('cpanel', value)

    @staticmethod
    def getPrivateId():
        return Config.getConfigValue('security', 'privateId')

    @staticmethod
    def getGroupId():
        return Config.getConfigValue('security', 'groupId')

    @staticmethod
    def getAdminList():
        adminList = {}

        for item in Config.getConfigValue('security', 'admList').split(','):
            var = item.split(':') 
            adminList[int(var[0])] = var[1]

        return adminList

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
