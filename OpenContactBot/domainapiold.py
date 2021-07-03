# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re, time
from log import Log
from mail import sendMail
from crypto import Crypto
from bs4 import BeautifulSoup
from config import Config as cfg
from robobrowser import RoboBrowser
from cache import save_obj,load_obj
from accountloader import getAccountsList
from cpanelapiclient import cpanelApiClient

listBlockHosting = []
listUnBlockHosting = []

hostingServerDmsList = { 
                        's2.open.by' : '2',
                        's3.open.by' : '3',
                        's4.open.by' : '5',
                        's5.open.by' : '8',
                        's6.open.by' : '9',
                        's7.open.by' : '12',
                        's8.open.by' : '13',
                        's9.open.by' : '14',
                        }

class DomainApiOld(object):
    dLog = Log('domainApi')

    url_search = 'https://domain.by/BackEnd/Support/Search.aspx'
    url = 'https://domain.by'

    def _get_form_post_data(self, browser):
        form = browser.get_form('aspnetForm')
        view_state = form['__VIEWSTATE']
        generator = form['__VIEWSTATEGENERATOR']
        validation = form['__EVENTVALIDATION']
        data = dict(
            __EVENTTARGET="",
            __EVENTARGUMENT="",
            __VIEWSTATE=view_state.value,
            __VIEWSTATEGENERATOR=generator.value,
            __EVENTVALIDATION=validation.value,
        )
        return data

    def getAuth(self):
        login_url = self.url + '/Authorization/Login'

        browser = RoboBrowser(parser='html.parser',history=True)
        browser.open(login_url)

        signin = browser.get_form(action=re.compile(r'\/Authorization\/Login'))
        signin["Login"].value = Crypto.getDomainUsername()
        signin["Password"].value = Crypto.getDomainPassword()
        browser.submit_form(signin)

        browser.open(self.url_search)

        if(browser.url == self.url_search):
            return browser
        else:
            self.dLog.critical("[getAuth] Авторизация не пройдена.Повторная попытка через 3 секунды...")
            time.sleep(3)
            return self.getAuth()

    def getDomainTasksList(self):

        browser  = self.getAuth()

        if(browser is None):
            return

        #Fix block error in dms
        if('ctl00_contentHolder_TaskList_ucStop_lblActionType' in browser.response.text):
            self.checkBlockError(browser)
        else:
            for blockHosting in listBlockHosting:
                self.dLog.info("[Domain.by] Исправлена ошибка блокировки в дмс: %s "%blockHosting.encode("utf-8").decode("idna"))
                self.openbot.sendMessageMe("[Domain.by] Исправлена ошибка блокировки в дмс: %s"%blockHosting.encode("utf-8").decode("idna"))

            listBlockHosting.clear()
            save_obj(listBlockHosting,'listBlockHosting')

        if('ctl00_contentHolder_TaskList_ucUnblock_lblActionType' in browser.response.text):
            self.checkUnBlockError(browser)
        else:
            for unBlockHosting in listUnBlockHosting:
                self.dLog.info("[Domain.by] Исправлена ошибка разблокировки в дмс: %s "%unBlockHosting.encode("utf-8").decode("idna"))
                self.openbot.sendMessageMe("[Domain.by] Исправлена ошибка разблокировки в дмс: %s"%unBlockHosting.encode("utf-8").decode("idna"))

            listUnBlockHosting.clear()
            save_obj(listUnBlockHosting,'listUnBlockHosting')
    
    def checkUnBlockError(self, browser):
        exclude_list = cfg.getExcludeDomainList()

        soup=BeautifulSoup(browser.response.text, "html.parser")

        haveValue = True
        i = 1

        temp = []
        while(haveValue):
            try:
                domain = soup.find(id="ctl00_contentHolder_TaskList_ucUnblock_rptServiceList_ctl0%s_lblDomain"%i).text.replace('www.', '')
                status = soup.find(id="ctl00_contentHolder_TaskList_ucUnblock_rptServiceList_ctl0%s_lblCpanelError"%i).text
                url_block = "https://domain.by/BackEnd/Support/" + soup.find(id="ctl00_contentHolder_TaskList_ucUnblock_rptServiceList_ctl0%s_hlAction"%i).get('href')

                if(status != "Ошибка"):
                    i += 1
                    continue

                if(re.search('[а-яА-Я]', domain)):
                    domain = domain.encode("idna").decode("utf-8")

                if(domain not in listUnBlockHosting):
                    self.dLog.info("[Domain.by] Обнаружена ошибка разблокировки: %s"%domain.encode("utf-8").decode("idna"))
                    self.openbot.sendMessageGroup("[Domain.by] Обнаружена ошибка разблокировки: %s"%domain.encode("utf-8").decode("idna"))
                    listUnBlockHosting.append(domain)

                    if(len(listUnBlockHosting) > 0):
                        save_obj(listUnBlockHosting,'listUnBlockHosting')

                    if(domain in exclude_list):
                        self.dLog.info("[Domain.by] [Ошибка разблокировки] %s в списке исключений."%domain.encode("utf-8").decode("idna"))
                        self.openbot.sendMessageGroup("[Domain.by] [Ошибка разблокировки]  %s в списке исключений."%domain.encode("utf-8").decode("idna"))
                        i += 1
                        continue

                    browser.open(url_block)

                    hosting = getAccountsList()[domain].server
                    self.dLog.info("[Domain.by] [Ошибка разблокировки] Расположен на сервере: %s"%hosting)

                    dataToPost = self._get_form_post_data(browser)
                    dataToPost["ctl00$contentHolder$HostingServersList$HostingServers"] = hostingServerDmsList[hosting]
                    dataToPost["ctl00$contentHolder$cbCpanelSynchro"] = "on"
                    dataToPost["ctl00$contentHolder$btnUnblock"] = "Разблокировать"

                    browser.open(url_block, method='post', data=dataToPost)

                    self.dLog.info('Для доменного имени %s необходимо произвести смену хостинг сервера на %s'%(domain.encode("utf-8").decode("idna"), hosting))
                    self.openbot.sendMessageGroup('Для доменного имени %s необходимо произвести смену хостинг сервера на %s'%(domain.encode("utf-8").decode("idna"), hosting))

                i += 1

            except KeyError as inst:
                i += 1
                self.dLog.critical("[checkUnBlockError] %s не найден на хостинге."%domain)
                self.openbot.sendMessageGroup("[checkUnBlockError] %s не найден на хостинге."%domain)
                pass
            except RuntimeError as inst:
                 self.dLog.critical("[checkUnBlockError] %s"%inst)
                 self.openbot.sendMessageGroup("[Domain.by][checkUnBlockError][RuntimeError]: %s"%(inst))
            except Exception as inst:
                haveValue = False

    def checkBlockError(self, browser):
        exclude_list = cfg.getExcludeDomainList()

        soup=BeautifulSoup(browser.response.text, "html.parser")

        haveValue = True
        i = 1

        temp = []
        while(haveValue):
            try:
                domain = soup.find(id="ctl00_contentHolder_TaskList_ucStop_rptServiceList_ctl0%s_lblDomain"%i).text.replace('www.', '')
                status = soup.find(id="ctl00_contentHolder_TaskList_ucStop_rptServiceList_ctl0%s_lblCpanelError"%i).text
                url_block = "https://domain.by/BackEnd/Support/" + soup.find(id="ctl00_contentHolder_TaskList_ucStop_rptServiceList_ctl0%s_hlAction"%i).get('href')

                if(status != "Ошибка"):
                    i += 1
                    continue

                if(re.search('[а-яА-Я]', domain)):
                    domain = domain.encode("idna").decode("utf-8")

                if(domain not in listBlockHosting):
                    self.dLog.info("[Domain.by] Обнаружена ошибка блокировки: %s"%domain.encode("utf-8").decode("idna"))
                    self.openbot.sendMessageGroup("[Domain.by] Обнаружена ошибка блокировки: %s"%domain.encode("utf-8").decode("idna"))
                    listBlockHosting.append(domain)
                    
                    if(len(listBlockHosting) > 0):
                        save_obj(listBlockHosting,'listBlockHosting')

                    if(domain in exclude_list):
                        self.dLog.info("[Domain.by] [Ошибка блокировки] %s в списке исключений."%domain.encode("utf-8").decode("idna"))
                        self.openbot.sendMessageGroup("[Domain.by] [Ошибка блокировки]  %s в списке исключений."%domain.encode("utf-8").decode("idna"))
                        i += 1
                        continue

                    browser.open(url_block)

                    hosting = getAccountsList()[domain].server
                    self.dLog.info("[Domain.by] [Ошибка блокировки] Расположен на сервере: %s"%hosting)

                    dataToPost = self._get_form_post_data(browser)
                    dataToPost["ctl00$contentHolder$HostingServersList$HostingServers"] = hostingServerDmsList[hosting]
                    dataToPost["ctl00$contentHolder$cbCpanelSynchro"] = "on"
                    dataToPost["ctl00$contentHolder$btnStop"] = "Блокировать"

                    browser.open(url_block, method='post', data=dataToPost)

                    self.dLog.info('Для доменного имени %s необходимо произвести смену хостинг сервера на %s'%(domain.encode("utf-8").decode("idna"), hosting))
                    self.openbot.sendMessageMe("[Domain.by] [Ошибка блокировки]  Для доменного имени %s необходимо произвести смену хостинг сервера на %s."%domain.encode("utf-8").decode("idna"), hosting)

                i += 1

            except KeyError as inst:
                i += 1
                self.dLog.critical("[checkBlockError] %s не найден на хостинге."%domain)
                self.openbot.sendMessageGroup("[checkBlockError] %s не найден на хостинге."%domain)
                pass
            except RuntimeError as inst:
                 self.dLog.critical("[checkBlockError] %s"%inst)
                 self.openbot.sendMessageGroup("[Domain.by][checkBlockError][RuntimeError]: %s"%(inst))
            except Exception as inst:
                haveValue = False

    def startDomainCheck(self, openbot):
        time.sleep(4)

        self.dLog.info('DomainApi started.')
        self.openbot = openbot
        
        while 1:
                try:
                    time.sleep(3600)
                    self.getDomainTasksList()
                except Exception as exc:
                    self.dLog.critical("[DomainApi] %s" % exc)
                    self.openbot.sendMessageMe("[DomainApi] %s" % exc)
