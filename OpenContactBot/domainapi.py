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

listDeleteHosting = []
listCreateHosting = []
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

class Service(object):
    def __init__(self, domain, state, date, contract, client, type, email, controlemail):
        self.domain = domain
        self.state = state
        self.date = date
        self.contract = contract
        self.client = client
        self.type = type
        self.email = email
        self.controlemail = controlemail

class DomainApi(object):
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
        login_url = self.url + '/Login.aspx'

        browser = RoboBrowser(parser='html.parser',history=True)
        browser.open(login_url)

        signin = browser.get_form(action=re.compile(r'\/Authorization\/Login'))
        signin["Login"].value = Crypto.getDomainUsername()
        signin["Password"].value = Crypto.getDomainPassword()
        browser.submit_form(signin)

        if(browser.url == self.url_search):
            return browser
        else:
            self.dLog.critical("[getAuth] Авторизация не пройдена.Повторная попытка через 3 секунды...")
            time.sleep(3)
            return self.getAuth()

    def getListofHostingServices(self, emailInTicket, active=True):
        browser = self.getAuth()

        cnameYandexMail = [
            'yandex.ru',
            'yandex.ua',
            'yandex.by',
            'yandex.kz',
            'yandex.com',
            'ya.ru'
        ]

        aliasListEmailFromTicket = []

        if(emailInTicket.split('@')[1] in cnameYandexMail):
            usernameEmail = emailInTicket.split('@')[0]
            
            for yaAlias in cnameYandexMail:
                aliasListEmailFromTicket.append('%s@%s'%(usernameEmail,yaAlias))
        else:
            aliasListEmailFromTicket.append(emailInTicket)
        
        listOfContract = set('')

        for emailFromAlias in aliasListEmailFromTicket:
            browser.open(self.url_search)
            request = browser.get_form(id='aspnetForm')
            request["ctl00$contentHolder$SearchContol$btnSearch"].value = 'Искать'
            request["ctl00$contentHolder$SearchContol$criteria"].value = 'email'
            request["ctl00$contentHolder$SearchContol$tbxInput"].value = emailFromAlias
            browser.submit_form(request)

            #Список идентификаторов клиента по контактной почте 
            listOfContract.update(set(re.findall('ctl00_contentHolder_DomainList_rptDomain_ctl\d\d_hlContract" href="\.\.\/\.\.\/Domains\/Services\?ClientId\=(.+?)\"', browser.response.text)))
        
        #Кабинет клиента с списком услуг
        clientCabinetUrl = 'https://domain.by/Domains/Services?ClientId='
        listOfHosting = []
        tempListOfHosting = []

        for clientId in listOfContract:
            browser.open(clientCabinetUrl + clientId)

            dataToPost = {
                "ClientId":clientId,
                "X-Requested-With":"XMLHttpRequest",  
                "page":1 
               }

            browser.open('https://domain.by/Domains/ShowPage?Length=7', method='post', data=dataToPost)

            #Добавляем все услуги хостинга из кабинета пользователя в общую переменную
            listOfHosting.extend(re.findall('openSansBold">(.+?)<\/div>\\r?\\n?\s{1,}?<div class="service_type openSansItalic">Виртуальный', browser.response.text))

        for hosting in set(listOfHosting):
            browser.open(self.url_search)
            request = browser.get_form(id='aspnetForm')
            request["ctl00$contentHolder$SearchContol$btnSearch"].value = 'Искать'
            request["ctl00$contentHolder$SearchContol$criteria"].value = 'hosting'
            request["ctl00$contentHolder$SearchContol$tbxInput"].value = hosting
            browser.submit_form(request)

            soup=BeautifulSoup(browser.response.text, "html.parser")

            haveValue = True
            i = 1
            
            while(haveValue):
                try:
                    temp = []
                    temp = (soup.find(id="ctl00_contentHolder_DomainList_rptDomain_ctl0%i_pEmail"%i).previous_element.parent.text).replace('\t','').replace('\n','').replace('\r\r','\r').splitlines()
                    controlEmail = (re.search('pEmail\"\>\\r\\n\\t\\r\\n\\t\\t\\t\<td class\=\"borderRight\"\>\\r\\n\\t\\t\\t\\t.{1,20}\@.{1,20}(\<br\/\>)?(.{1,20}\@.{1,20})?\\r', browser.response.text).group(0)[46:-1]).split('<br/>')

                    domain = temp[0]
                    state = temp[1]
                    date = temp[2]
                    contract = temp[3]
                    client = temp[4]
                    type = temp[-2]
                    email = temp[-1]


                    if(re.search('[а-яА-Я]', domain)):
                        domain = domain.encode("idna").decode("utf-8")

                    if(state == 'оплачен' or state == 'приостановлен' or not active):
                        tempListOfHosting.append(Service(domain, state, date, contract, client, type, email, controlEmail))
                    else:
                        self.dLog.critical("Пропущена услуга: Домен:%s Статус:%s" %(domain,state))
                        self.openbot.sendMessageMe("Пропущена услуга: Домен:%s Статус:%s" %(domain,state))

                    i += 1
                except AttributeError:
                    haveValue = False
                except Exception as exc:
                    self.dLog.critical("[getListofServices] %s" % exc)
                    self.openbot.sendMessageMe("[getListofServices] %s" % exc)

        return tempListOfHosting

    def getListofServices(self, criteria, domain, active=True):
        browser = self.getAuth()
        browser.open(self.url_search)

        request = browser.get_form(id='aspnetForm')
        request["ctl00$contentHolder$SearchContol$btnSearch"].value = 'Искать'
        request["ctl00$contentHolder$SearchContol$criteria"].value = criteria
        request["ctl00$contentHolder$SearchContol$tbxInput"].value = domain
        browser.submit_form(request)

        soup=BeautifulSoup(browser.response.text, "html.parser")

        haveValue = True
        list = []
        i = 1

        while(haveValue):
            temp = []
            try:
                temp = (soup.find(id="ctl00_contentHolder_DomainList_rptDomain_ctl0%s_pEmail"%i).previous_element.parent.text).replace('\t','').replace('\n','').replace('\r\r','\r').splitlines()
                controlEmail = (re.search('pEmail\"\>\\r\\n\\t\\r\\n\\t\\t\\t\<td class\=\"borderRight\"\>\\r\\n\\t\\t\\t\\t.{1,20}\@.{1,20}(\<br\/\>)?(.{1,20}\@.{1,20})?\\r', browser.response.text).group(0)[46:-1]).split('<br/>')

                domain = temp[0]
                state = temp[1]
                date = temp[2]
                contract = temp[3]
                client = temp[4]

                #NOT IMPLEMENT state 'ожидает активации'
                if(state == 'заказ' or state == 'оплачен' or state == 'приостановлен'):
                    type = temp[6]
                    email = temp[7]

                try:
                   #Отсутсвует поле домена и состояния
                   int(domain)

                   url_contract = "https://domain.by/BackEnd/Support/" + soup.find(id="ctl00_contentHolder_DomainList_rptDomain_ctl0%s_hlContract"%i).get('href')
                   clienId = re.search('Services\?ClientId\=(.+?)$', url_contract).group(1)

                   data = {
                       "ClientId":clienId,
                       "X-Requested-With":"XMLHttpRequest",
                       "page":1
                       } 

                   browser.open(url_contract)
                   browser.open('https://domain.by/Domains/ShowPage?Length=7', method='post', data=data)

                   domain = re.search('\<a class\=\"list_link\" href\=\"\/Settings\/Hosting\.aspx\?serviceId\=\d{1,10}\"\>(.+?)\<\/a\>', browser.response.text).group(1)
                except ValueError:
                   self.dLog.critical("[getListofServices] Имя домена было определено неккоректно.")
                   i += 1
                   continue

                if(state == 'оплачен' or not active):
                    list.append(Service(domain, state, date, contract, client, type, email, controlEmail))

                i += 1
            except AttributeError:
                haveValue = False
            except Exception as exc:
                self.dLog.critical("[getListofServices] %s" % exc)
                self.openbot.sendMessageMe("[getListofServices] %s" % exc)

        return list

    def removeFromExcludeList(self, domain):
        exclude_list = cfg.getExcludeDomainList()

        if(domain not in exclude_list):
            return

        exclude_list = list(filter(lambda a: a != domain, exclude_list))
        cfg.setConfigValue('exclude', 'create', ",".join(exclude_list))
        cfg.saveConfig()

        self.dLog.info("[Domain.by] Аккаунт хостинга удален из исключений: %s"%domain)
        self.openbot.sendMessageGroup("[Domain.by] Аккаунт хостинга удален из исключений: %s"%domain)

    def getDomainTasksList(self):
        global listCreateHosting
        global listDeleteHosting

        browser  = self.getAuth()

        if(browser is None):
            return

        if('ctl00_contentHolder_TaskList_ucDelete_lblActionType' in browser.response.text):
            try:
                self.checkDeleteHosting(browser.response.text, browser)
            except Exception as exc:
                self.dLog.critical("[checkDeleteHosting] %s"%exc)
        else:
            for deleteHosting in listDeleteHosting:
                self.dLog.info("[Domain.by] хостинг удалён: %s "%deleteHosting.encode("utf-8").decode("idna"))
                self.openbot.sendMessageGroup("[Domain.by] хостинг удалён: %s"%deleteHosting.encode("utf-8").decode("idna"))

            listDeleteHosting.clear()
            save_obj(listDeleteHosting,'listDeleteHosting')

        #Fix block error in dms
        if('ctl00_contentHolder_TaskList_ucStop_lblActionType' in browser.response.text):
            self.checkBlockError(browser)
        else:
            for blockHosting in listBlockHosting:
                self.dLog.info("[Domain.by] Исправлена ошибка блокировки в дмс: %s "%blockHosting.encode("utf-8").decode("idna"))
                self.openbot.sendMessageMe("[Domain.by] Исправлена ошибка блокировки в дмс: %s"%blockHosting.encode("utf-8").decode("idna"))

            listBlockHosting.clear()
            save_obj(listBlockHosting,'listDeleteHosting')

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

    def checkDeleteHosting(self, value, browser):
        global listDeleteHosting
        tempListDeleteHosting = []
        exclude_list = cfg.getExcludeDomainList()

        soup=BeautifulSoup(value, "html.parser")

        haveValue = True
        i = 1

        while(haveValue):
            try:
                domain = soup.find(id="ctl00_contentHolder_TaskList_ucDelete_rptServiceList_ctl0%s_lblDomain"%i).text

                if(re.search('[а-яА-Я]', domain)):
                    domain = domain.encode("idna").decode("utf-8")

                if(domain not in exclude_list and domain in listDeleteHosting):
                    listDeleteHosting.remove(domain)

                tempListDeleteHosting.append(domain)
                
                if(domain not in listDeleteHosting):
                    self.dLog.info("[Domain.by] хостинг на удаление: %s"%domain.encode("utf-8").decode("idna"))
                    self.openbot.sendMessageGroup("[Domain.by] хостинг на удаление: %s"%domain.encode("utf-8").decode("idna"))
                    listDeleteHosting.append(domain)

                    if(domain in exclude_list):
                        self.dLog.info("[Domain.by] %s в списке исключений."%domain.encode("utf-8").decode("idna"))
                        self.openbot.sendMessageGroup("[Domain.by] %s в списке исключений."%domain.encode("utf-8").decode("idna"))
                        continue

                    cpanelUsersAccounts = getAccountsList()

                    hosting = cpanelUsersAccounts[domain].server
                    username = cpanelUsersAccounts[domain].username
                    self.dLog.info("[Domain.by] Расположен на сервере: %s"%hosting)
                    self.dLog.info("[Domain.by] Имя аккаунта: %s"%username)

                    #Implement api query to remove hosting, after add list exception.
                    answer = cpanelApiClient[hosting].call('removeacct',user=username)['result'][0]
                    status = int(answer['status'])
                    message = answer['statusmsg']

                    if(status == 1 or "does not exist!" in message):
                        url_delete = "https://domain.by/BackEnd/Support/" + soup.find(id="ctl00_contentHolder_TaskList_ucDelete_rptServiceList_ctl0%s_hlAction"%i).get('href')
                        
                        browser.open(url_delete)
                        delete = browser.get_form(id='aspnetForm')
                        browser.submit_form(delete, submit=delete['ctl00$contentHolder$btnDelete'])

                        if(browser.url == self.url_search):
                            self.dLog.info("[Domain.by] Задача удаления завершена: %s"%username)

                    else:
                        self.dLog.critical("[checkDeleteHosting][Cpanel] %s"%message)
                        self.openbot.sendMessageGroup("[Domain.by] Хостинг не удален: %s .\nТекст ответа: %s"%(domain.encode("utf-8").decode("idna"), message))

            except KeyError as inst:
                exclude_list.append(domain)

                cfg.setConfigValue('exclude', 'create', ",".join(exclude_list))
                cfg.saveConfig()

                self.dLog.critical("[checkDeleteHosting][KeyError] %s добавлен в список исключений, так как не найден на сервере."%domain.encode("utf-8").decode("idna"))
                self.openbot.sendMessageGroup("[checkDeleteHosting][KeyError] %s добавлен в список исключений, так как не найден на сервере."%domain.encode("utf-8").decode("idna"))
            except RuntimeError as inst:
                 self.dLog.critical("[checkDeleteHosting][Cpanel] %s"%inst)
                 self.openbot.sendMessageGroup("[Domain.by][RuntimeError]: %s"%(inst))
            except Exception as inst:
                haveValue = False
            finally:
                i += 1

        deletedHosting = set(listDeleteHosting) ^ set(tempListDeleteHosting)
        
        for dHosting in deletedHosting:
            self.dLog.info("[Domain.by] хостинг удалён: %s "%dHosting.encode("utf-8").decode("idna"))
            self.openbot.sendMessageGroup("[Domain.by] хостинг удалён: %s"%dHosting.encode("utf-8").decode("idna"))

        listDeleteHosting = tempListDeleteHosting
        save_obj(listDeleteHosting,'listDeleteHosting')

    def loadListDeleteCachedValues(self):
        global listDeleteHosting

        try:
            temp = load_obj('listDeleteHosting')

            if (len(temp) > 0):
                listDeleteHosting = temp
        except:
            pass
    def loadListCreateCachedValues(self):
        global listCreateHosting

        try:
            temp = load_obj('listCreateHosting')

            if (len(temp) > 0):
                listCreateHosting = temp
        except:
            pass

    def startDomainCheck(self, openbot):
        time.sleep(4)

        self.dLog.info('DomainApi started.')
        self.openbot = openbot

        self.loadListDeleteCachedValues()
        self.loadListCreateCachedValues()
        
        while 1:
                try:
                    time.sleep(180)
                    self.getDomainTasksList()
                except Exception as exc:
                    self.dLog.critical("[DomainApi] %s" % exc)
                    self.openbot.sendMessageMe("[DomainApi] %s" % exc)

