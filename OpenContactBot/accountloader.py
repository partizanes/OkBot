# -*- coding: utf-8 -*-
# by Part!zanes 2017
 
from time import sleep
from cpanelapiclient import cpanelApiClient
from cpaneluser import cpanelUser
from log import Log
from cache import *

def loadDataFromServers():

    if not (isOutdated('cpanelUsersAccounts')):
            loadFromCache()
            return

    log.info("Loading Account list...")

    global cpanelUsersAccounts

    for hosting,client in cpanelApiClient.items():
        try:
            answeData = client.call_v1('listaccts')
        except Exception as exc:
            log.critical(exc)

        for accountData in (answeData['data']['acct']):
            cpanelUsersAccounts[accountData['domain']] =  cpanelUser(accountData['user'], accountData['domain'], hosting, accountData['email'])

    if(len(cpanelUsersAccounts) > 0):
        save_obj(cpanelUsersAccounts,'cpanelUsersAccounts')

    log.info("...completed.Found %s accounts" %(len(cpanelUsersAccounts)))

def reloadData():
    global cpanelUsersAccounts
    
    log.info("Cleanup cpanelUsersAccounts...")
    cpanelUsersAccounts.clear()
    log.info("...cleaned")
    loadDataFromServers()

def cronReloadListAccounts():
    while 1:
        sleep(30)
        timer = int(getTimeToStartCron('cpanelUsersAccounts'))
        log.info("Cron started.Time to reload: %s minutes." %(int(timer/60)))
        sleep(timer)
        reloadData()

def loadFromCache():
    global cpanelUsersAccounts

    log.info("Loading Account list from cache...")
    cpanelUsersAccounts = load_obj('cpanelUsersAccounts')
    log.info("...completed.Found %s accounts" %(len(cpanelUsersAccounts)))

def getAccountsList():
    return cpanelUsersAccounts

log = Log('cpanelUsersAccounts')
cpanelUsersAccounts = {}