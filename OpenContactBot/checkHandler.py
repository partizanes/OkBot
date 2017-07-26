# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re
import sys
import time
from log import Log
from ticket import Ticket
from datebase import Datebase
from accountloader import *
from cpanelapiclient import cpanelApiClient
from openbot import openbot
from config import Config


class CheckHandler(object):
    CheckHandlerLog = Log('CheckHandler')
    
    def parseDomainbyTask(self, ticket):
        try:
            domain = re.search(u'Изменение тарифного плана виртуального хостинга для домена (.+?)</td>', ticket.message).group(1)
            #prevPackage  = re.search(u'с плана \"(.+?)" на план', ticket.message).group(1)
            afterPackage  = re.search(u'на план \"(.+?)"\.<br', ticket.message).group(1)

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
                self.CheckHandlerLog.critical("[Package][%s][%s] %s." %(ticket.ticket_id, domain, message))
                self.openbot.sendMessageMe("[Package][%s][%s] %s. " %(ticket.ticket_id, domain, message))
        except Exception as inst:
            self.CheckHandlerLog.critical(inst)
            self.CheckHandlerLog.critical(sys.exc_info()[0])

    def getListTickets(self):
        try:
            list = []
            results = Datebase().getNewTicketsRows()

            for row in results:
                list.append(Ticket(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

            return list
        except Exception as inst:
            self.CheckHandlerLog.critical(inst)
            self.CheckHandlerLog.critical(sys.exc_info()[0])

    def checkNewMessage(self):
        for ticket in self.getListTickets():
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
            if re.match("\[s.\.open.by\] Disk Usage Warning: The user", ticket.subject):
                self.CheckHandlerLog.info("[Квота][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("Квота[%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"\<\!\-\- head not allowed \-\->Домен\: \w{1,25}(\.\w{1,25})?\.\w{1,5}\; Сервер\: http(s)?\:\/\/s\d\.open\.by\:2087\/json\-api\/\; Действие: Успешно заблокирован", ticket.message):
                self.CheckHandlerLog.info("[API block][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[API block][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"\<\!\-\- head not allowed \-\->Домен\: \w{1,25}(\.\w{1,25})?\.\w{1,5}\; Сервер\: http(s)?\:\/\/s\d\.open\.by\:2087\/json\-api\/\; Действие: Успешно разблокирован", ticket.message):
                self.CheckHandlerLog.info("[API unblock][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[API unblock][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if (ticket.client_id == 94434):
                self.parseDomainbyTask(ticket)
                continue

    def start(self):
        self.CheckHandlerLog.info('CheckHandler started.')
        self.openbot = openbot

        loadDataFromServers()

        while 1:
            self.checkNewMessage()
            time.sleep(30)
        

   