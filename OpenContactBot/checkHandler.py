# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re
import sys
import time
from datebase import Datebase
from log import Log
from ticket import Ticket


class CheckHandler(object):
    CheckHandlerLog = Log('CheckHandler')
    
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
            #else:
                #self.openbot.sendMessageGroup("[%s] Новая заявка \n %s \n %s" % (ticket.ticket_id,ticket.subject,ticket.message))

    def start(self, openbot):
        self.CheckHandlerLog.info('CheckHandler started.')
        self.openbot = openbot

        while 1:
            self.checkNewMessage()
            time.sleep(30)
        

   