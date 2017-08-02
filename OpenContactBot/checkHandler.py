# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re
import sys
import time
from log import Log
from ticket import Ticket
from datebase import Datebase
from accountloader import loadDataFromServers
from accountloader import getAccountsList
from cpanelapiclient import cpanelApiClient
from config import Config
from cache import save_obj
from cache import load_obj
from openbot import openbot
from ticket import activeTickets

class CheckHandler(object):
    CheckHandlerLog = Log('CheckHandler')
    
    def loadCacheActiveTasks(self):
        global activeTickets

        try:
            temp = load_obj('activeTickets')

            if (len(temp) > 0):
                activeTickets = temp
        except:
            pass

    def parseDomainbyTask(self, ticket):
        if re.match(u'Ошибки при автоматическом запуске хостинга', ticket.subject):
            try:
                error = re.search(u'Error: There was an error:\n(.+?)<br \/>', ticket.message).group(1)

                if('Время ожидания операции истекло' in error):
                    self.CheckHandlerLog.info("[Таймаут][%s] Закрыт" % ticket.ticket_id)
                    self.openbot.sendMessageMe("[Таймаут][%s] Закрыт" % ticket.ticket_id)
                    Datebase().setTicketClose(ticket.ticket_id)
                    return
                else:
                    self.CheckHandlerLog.info("[Таймаут][%s] Ошибка: %s" %(ticket.ticket_id, error))
                    self.openbot.sendMessageMe("[Таймаут][%s] Ошибка: %s" %(ticket.ticket_id, error))

            except Exception as inst:
                self.CheckHandlerLog.critical("[parseDomainbyTask][запуск хостинга] %s" %(inst))
                self.CheckHandlerLog.critical(sys.exc_info()[0])

        if re.match(u'Изменение тарифного плана виртуального хостинга для домена', ticket.subject) or (re.search(u'\<td\>В ДМС изменен тарифный план виртуального хостинга для домена', ticket.message) is not None):
            try:
                domain = re.search(u'Изменение тарифного плана виртуального хостинга для домена (.+?)</td>', ticket.message).group(1)
                #prevPackage  = re.search(u'с плана \"(.+?)" на план', ticket.message).group(1)
                afterPackage  = re.search(u'на план \"(.+?)"\.<br', ticket.message).group(1)

                cpanelUsersAccounts = getAccountsList()
                hosting = cpanelUsersAccounts[domain].server
                username = cpanelUsersAccounts[domain].username

                answer = cpanelApiClient[hosting].call('changepackage',user=username,pkg=afterPackage)['result'][0]
                status = int(answer['status'])
                message = answer['statusmsg']
                #self.CheckHandlerLog.info("[Package][%s] Сообщение: %s" %(domain , message))

                if(status == 1):
                    self.CheckHandlerLog.info("[Package][%s][%s] смена тарифного плана. " %(ticket.ticket_id, domain))
                    self.openbot.sendMessageMe("[Package][%s][%s] смена тарифного плана. " %(ticket.ticket_id, domain))
                    Datebase().setTicketClose(ticket.ticket_id)
                else:
                    self.CheckHandlerLog.critical("[Package][%s][%s] %s." %(ticket.ticket_id, domain, ticket.message))
                    self.openbot.sendMessageMe("[Package][%s][%s] %s. " %(ticket.ticket_id, domain, ticket.message))
            except Exception as inst:
                self.CheckHandlerLog.critical("[Package] %s" %(inst))
                self.CheckHandlerLog.critical(sys.exc_info()[0])
        else:
            self.CheckHandlerLog.critical("[parseDomainbyTask][%s] Заявка не классифицирована." %(ticket.ticket_id))
            self.openbot.sendMessageMe("[parseDomainbyTask][%s] Заявка не классифицирована. " %(ticket.ticket_id))

    def getListTickets(self):
        try:
            list = []
            results = Datebase().getNewTicketsRows()

            for row in results:
                list.append(Ticket(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

            return list
        except Exception as inst:
            self.CheckHandlerLog.critical("[getListTickets] %s" %(inst))
            self.CheckHandlerLog.critical(sys.exc_info()[0])

    def undefinedTicket(self, ticket):
        if (ticket.ticket_id not in activeTickets):
            activeTickets[ticket.ticket_id] = ticket
            self.CheckHandlerLog.info("[Ticket][%s] Новая Заявка.\n %s \n %s \n %s" %(ticket.ticket_id, ticket.email, ticket.subject, ticket.message))
            #self.openbot.sendMessageMe("[Ticket][%s] Новая Заявка.\n %s \n %s \n %s" %(ticket.ticket_id, ticket.email, ticket.subject, ticket.message))
            self.openbot.sendMessageGroup("[Ticket][%s] Новая Заявка.\n %s \n %s \n %s" %(ticket.ticket_id, ticket.email, ticket.subject, ticket.message))
        #else:
            #self.CheckHandlerLog.debug("[Ticket][%s] Заявка уже содержится в списке." % ticket.ticket_id)

    def checkNewMessage(self):
        tickets  = self.getListTickets()

        global activeTickets

        try:
            closedTickets = {k: activeTickets[k] for k  in activeTickets.keys() ^ set(ticket.ticket_id for ticket in tickets)}

            for cTicket in closedTickets:
                self.CheckHandlerLog.info("[Заявка][%s] обработана вручную." % cTicket)
                self.openbot.sendMessageMe("[Заявка][%s] обработана вручную." % cTicket)
        except KeyError:
            pass
            #self.CheckHandlerLog.critical("[checkNewMessage] %s" %(inst))
            #self.CheckHandlerLog.critical(sys.exc_info()[0]) 

        activeTickets = {k: activeTickets[k] for k  in activeTickets.keys() & set(ticket.ticket_id for ticket in tickets)}
        save_obj(activeTickets,'activeTickets')

        if not tickets:
            return

        for ticket in tickets:
            time.sleep(0.5)
            if re.match("\[s.\.open.by\] New account: \w{1,16}", ticket.subject):
                self.CheckHandlerLog.info("[Создание][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[Создание][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match("\[s.\.open.by\] Account Suspended: \w{1,16}", ticket.subject):
                self.CheckHandlerLog.info("[Блокировка][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[Блокировка][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match("\[s.\.open.by\] Account Unsuspended: \w{1,16}", ticket.subject):
                self.CheckHandlerLog.info("[Pазблокировка][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[Pазблокировка][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match("\[s.\.open.by\] Disk Usage Warning: The user", ticket.subject):
                self.CheckHandlerLog.info("[Квота][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("Квота[%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"\<\!\-\- head not allowed \-\->Домен\: \w{1,25}(-)?(\.)?(\w{1,25})?(\.)?\w{1,5}\; Сервер\: http(s)?\:\/\/s\d\.open\.by\:2087\/json\-api\/\; Действие: Успешно заблокирован", ticket.message):
                self.CheckHandlerLog.info("[API block][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[API block][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"\<\!\-\- head not allowed \-\->Домен\: \w{1,25}(-)?(\.)?(\w{1,25})?(\.)?\w{1,5}\; Сервер\: http(s)?\:\/\/s\d\.open\.by\:2087\/json\-api\/\; Действие: Успешно разблокирован", ticket.message):
                self.CheckHandlerLog.info("[API unblock][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[API unblock][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if (ticket.client_id == 94434):
                self.parseDomainbyTask(ticket)
                continue
            else:
                self.undefinedTicket(ticket)


    def start(self):
        self.CheckHandlerLog.info('CheckHandler started.')
        self.openbot = openbot

        loadDataFromServers()
        self.loadCacheActiveTasks()

        while 1:
            self.checkNewMessage()
            time.sleep(30)
        

   