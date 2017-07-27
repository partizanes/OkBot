# -*- coding: utf-8 -*-
# by Part!zanes 2017
 
from time import sleep
from cpanelapiclient import cpanelApiClient
from cpaneluser import cpanelUser
from log import Log

def loadDataFromServers():
    log.info("Loading Account list...")

    global CpanelAccountList

    for hosting,client in cpanelApiClient.items():
        for accountData in (client.call('listaccts')['acct']):
            cpanelUsersAccounts[accountData['domain']] =  cpanelUser(accountData['user'], accountData['domain'], hosting)

    log.info("...completed.Found %s accounts" %(len(cpanelUsersAccounts)))

def reloadData():
    global CpanelAccountList
    
    log.info("Cleanup cpanelUsersAccounts...")
    cpanelUsersAccounts.clear()
    log.info("...cleaned")
    loadDataFromServers()


def cronReloadListAccounts():
    while 1:
        sleep(30)
        log.info("Cron started.Next reload after 5 hours.")
        sleep(18000)
        reloadData()


log = Log('CpanelAccountList')
cpanelUsersAccounts = {}