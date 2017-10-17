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
from cache import save_obj, load_obj
from ticket import activeTickets,activeRepTickets

class CheckHandler(object):
    CheckHandlerLog = Log('CheckHandler')

    def loadCacheActiveTasks(self):
        try:
            cache = load_obj('activeTickets')

            for i in cache:
                activeTickets[i] = cache[i]

            self.CheckHandlerLog.info("[Cache] activeTickets загружен.")
        except Exception as exc:
            pass

    def loadCacheActiveReply(self):
        try:
            cache = load_obj('activeRepTickets')

            for i in cache:
                activeRepTickets[i] = cache[i]

            self.CheckHandlerLog.info("[Cache] activeRepTickets загружен.")
        except Exception as exc:
            pass

    def managerParse(self, ticket):
        self.CheckHandlerLog.info("[Dashka][%s] Dashkaaaa detected :D" % ticket.ticket_id)
        self.openbot.sendMessageMe("[Dashka][%s] Dashkaaaa detected :D" % ticket.ticket_id)

        if(re.match(u'Смена\s{1,}(ТП)?(тарифного)?'),ticket.subject):
            try:
                _domain = re.search('\s[a-zA-Z]{1,15}((-|\.)[a-zA-Z]{1,10})?((-|\.)[a-zA-Z]{1,10})?\.([a-zA-Z]{1,6})(\.|\s)', message).group(0)
                _package = re.search('на (xS|S|M|L|XXL|MAX)', message).group(0).split()[1]

                cpanelUsersAccounts = getAccountsList()
                hosting = cpanelUsersAccounts[_domain].server
                username = cpanelUsersAccounts[_domain].username

                answer = cpanelApiClient[hosting].call('changepackage',user=username,pkg=_package)['result'][0]
                status = int(answer['status'])
                message = answer['statusmsg']

                if(status == 1):
                    self.CheckHandlerLog.info("[managerParse][%s][%s] смена тарифного плана. " % (ticket.ticket_id, _domain))
                    self.openbot.sendMessageMe("[managerParse][%s][%s] смена тарифного плана. " % (ticket.ticket_id, _domain))
                    hdapi.postQuickReply(ticket_id, "[OpenContactBot] Тарифный план изменен на %s для домена: %s "%(_package, _domain) , HdTicketStatus.CLOSED, self)
                    return True
                else:
                    self.CheckHandlerLog.critical("[managerParse][%s][%s] %s." % (ticket.ticket_id, _domain, ticket.message))
                    self.openbot.sendMessageMe("[managerParse][%s][%s] %s. " % (ticket.ticket_id, _domain, ticket.message))
            except Exception as inst:
                self.CheckHandlerLog.critical("[managerParse] %s" % (inst))
                self.CheckHandlerLog.critical("[managerParse] %s" % (ticket.subject))
                self.CheckHandlerLog.critical("[managerParse] %s" % (ticket.message))
        
        return False

    def parseDomainbyTask(self, ticket):
        if re.match(u'Ошибки при автоматическом запуске хостинга', ticket.subject):
            try:
                if('Время ожидания операции истекло' in ticket.message):
                    self.CheckHandlerLog.info("[Таймаут][%s] Закрыт" % ticket.ticket_id)
                    self.openbot.sendMessageMe("[Таймаут][%s] Закрыт" % ticket.ticket_id)
                elif('Данного хостинга нету на сервере' in ticket.message):
                    self.CheckHandlerLog.info("[Таймаут][%s] Закрыт. Необходимо вручную поменять сервер на domain.by для данного аккаунта. При следущем детекте добавить соответсвующую обработку" % ticket.ticket_id)
                    self.openbot.sendMessageGroup("[Таймаут][%s] Закрыт. Необходимо вручную поменять сервер на domain.by для данного аккаунта. При следущем детекте добавить соответсвующую обработку" % ticket.ticket_id)
                else:
                    self.CheckHandlerLog.info("[Таймаут][%s] Ошибка: %s" % (ticket.ticket_id, error))
                    self.openbot.sendMessageMe("[Таймаут][%s] Ошибка: %s" % (ticket.ticket_id, error))

                Datebase().setTicketClose(ticket.ticket_id)
                return

            except Exception as inst:
                self.CheckHandlerLog.critical("[parseDomainbyTask][запуск хостинга] %s" % (inst))
                self.CheckHandlerLog.critical(sys.exc_info()[0])
            
        if re.match(u'Изменение тарифного плана виртуального хостинга для домена', ticket.subject) or (re.search(u'\<td\>В ДМС изменен тарифный план виртуального хостинга для домена', ticket.message) is not None):
            try:
                domain = re.search(u'Изменение тарифного плана виртуального хостинга для домена (.+?)</td>', ticket.message).group(1)
                #prevPackage = re.search(u'с плана \"(.+?)" на план',ticket.message).group(1)
                afterPackage = re.search(u'на план \"(.+?)"\.<br', ticket.message).group(1)

                cpanelUsersAccounts = getAccountsList()
                hosting = cpanelUsersAccounts[domain].server
                username = cpanelUsersAccounts[domain].username

                answer = cpanelApiClient[hosting].call('changepackage',user=username,pkg=afterPackage)['result'][0]
                status = int(answer['status'])
                message = answer['statusmsg']
                #self.CheckHandlerLog.info("[Package][%s] Сообщение: %s" %(domain , message))

                if(status == 1):
                    self.CheckHandlerLog.info("[Package][%s][%s] смена тарифного плана. " % (ticket.ticket_id, domain))
                    self.openbot.sendMessageMe("[Package][%s][%s] смена тарифного плана. " % (ticket.ticket_id, domain))
                    Datebase().setTicketClose(ticket.ticket_id)
                else:
                    self.CheckHandlerLog.critical("[Package][%s][%s] %s." % (ticket.ticket_id, domain, ticket.message))
                    self.openbot.sendMessageMe("[Package][%s][%s] %s. " % (ticket.ticket_id, domain, ticket.message))
            except Exception as inst:
                self.CheckHandlerLog.critical("[Package] %s" % (inst))
                self.CheckHandlerLog.critical(sys.exc_info()[0])
        else:
            self.CheckHandlerLog.critical("[parseDomainbyTask][%s] Заявка не классифицирована." % (ticket.ticket_id))
            self.openbot.sendMessageMe("[parseDomainbyTask][%s] Заявка не классифицирована. " % (ticket.ticket_id))

    def getListTickets(self):
        try:
            list = []
            results = Datebase().getNewTicketsRows()

            for row in results:
                list.append(Ticket(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], self.getTicketAttachments(row[0])))

            return list
        except Exception as inst:
            self.CheckHandlerLog.critical("[getListTickets] %s" % (inst))
            self.CheckHandlerLog.critical(sys.exc_info()[0])
    
    def getTicketAttachments(self, ticket_id):
        dict = {}
        results = Datebase().getNewTicketAttachments(ticket_id)

        for row in results:
            dict[row[1]] = "http://hd.ok.by/admin/ticket_attachments.php?ticket_id=%s&att_id=%s"%(ticket_id, row[0])

        return dict

    def undefinedTicket(self, ticket):
        if (ticket.ticket_id not in activeTickets):
            activeTickets[ticket.ticket_id] = ticket
            ticket.message =  self.cleanUpMessage(ticket.message)

            #append attachments to message 
            for k, v in ticket.attachment.items():
                ticket.message += "\n<a href=\"%s\">%s</a>"%(v,k)

            self.CheckHandlerLog.info("[Ticket][%s] Новая Заявка.\n %s \n %s \n %s" % (ticket.ticket_id, ticket.email, ticket.subject, ticket.message))
            self.openbot.sendMessageGroup("[Ticket][%s] Новая Заявка.\n %s \n %s \n %s" % (ticket.ticket_id, ticket.email, ticket.subject, ticket.message), 'HTML', False)
            save_obj(activeTickets,'activeTickets')

    def cleanUpMessage(self, message):

        message = re.sub(r'<br>|</p>','\n', message)
        message = re.sub("<br />|</div>",' ', message)
        message = re.sub("<.*?>","", message)

        reg1 = re.compile(r"^[a-zA-zа-яА-ЯёЁ]+\,\s\d{2,2}\s\D+\s\d{4}\s\D\.\,\s\d{2,2}:\d{2,2}\s.*$", re.M)
        reg2 = re.compile(r"^\-{2,}\D\-{2,}.*$", re.M)
        reg3 = re.compile(r"^[\d]{2,2}.[\d]{2,2}.[\d]{4,4}\s[\d]{2,2}:[\d]{2,2},\s\D.*$", re.M)
        reg4 = re.compile(r"^[\d]{2,2}:[\d]{2,2},\s[\d]{2,2}\s\D+\d{4,4}\s\D.,\s\D.*$", re.M)
        reg5 = re.compile(r"^\d{1,}\D+\d{4,4}\s\D\.\,\s\d{1,}:\d{1,}\s\D.*$", re.M)
        reg6 = re.compile(r"^[a-zA-Zа-яА-ЯёЁ]+\d{2,2}.\d{2,2}.\d{4,4}\s\d{2,2}:\d{2,2},\s\D.*$", re.M)
        reg7 = re.compile(r"^[A-Za-zА-Яа-яеЁ]+,\s[\d]{1,}\s[A-Za-zА-Яа-яеЁ]+\s\d{4}\s[г]\.\,\s.*$", re.M)
        reg8 = re.compile(r"^[A-Za-zА-Яа-яеЁ]+\s[\d]{2,2}.[\d]{2,2}.[\d]{4,4}\s[\d]{2,2}:[\d]{2,2},\s[A-Za-zА-Яа-яеЁ]+.*$", re.M)
        reg9 = re.compile(r"^[\d]{1,}\s[A-Za-zА-Яа-яеЁ]+\.\s[\d]{4,4}\s[\D].\s[\d]{1,}:[\d]{1,}\s[A-Za-zА-Яа-яеЁ]+.*$", re.M)
        reg10 = re.compile(r"^>[\D\d].*$", re.M)
        reg11 = re.compile(r"\n{1,}")
        reg12 = re.compile(r"^\-{2,}.*$", re.M)
        reg13 = re.compile(r"^\_{2,}.*$", re.M)

        if reg10.findall(message):
            message = reg10.sub('\n', message).strip('\n')

        reglist = [reg1.findall(message), reg2.findall(message), reg3.findall(message), reg4.findall(message), reg5.findall(message), reg6.findall(message), reg7.findall(message), reg8.findall(message), reg9.findall(message)]
        for each in reglist:
            if(len(each) > 0):
                message = ''.join(message.split((''.join(each[0])), 1)[:-1])

        if reg12.findall(message):
            message = reg12.sub('\n', message).strip('\n')

        if reg13.findall(message):
            message = reg13.sub('\n', message).strip('\n')

        if reg11.findall(message):
            message = reg11.sub('\n', message).strip('\n')

        return message

    def checkNewReplies(self):
        replied_tickets = Datebase().getRepliesTicketsIdList()

        if(len(activeRepTickets) != 0):
            try:
                closedTickets = {k: activeRepTickets[k] for k  in activeRepTickets.keys() ^ set(replied_tickets)}

                for rTicket in closedTickets:
                    self.CheckHandlerLog.info("[Ответ][%s] закрыт." % rTicket)
                    self.openbot.sendMessageGroup("[Ответ][%s] закрыт." % rTicket)
            except KeyError:
                pass

            diff_ticket = {k: activeRepTickets[k] for k  in activeRepTickets.keys() & set(replied_tickets)}
            
            activeRepTickets.clear()

            for i in diff_ticket:
                activeRepTickets[i] = diff_ticket[i]

            save_obj(activeRepTickets,'activeRepTickets')

        for rTicket in replied_tickets:
            if rTicket not in activeRepTickets:
                time.sleep(0.5)

                for row in Datebase().getLastRepliesByTicketId(rTicket):
                    ticket = Ticket(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])

                    ticket.message = self.cleanUpMessage(ticket.message)

                    activeRepTickets[ticket.ticket_id] = ticket
                    save_obj(activeRepTickets,'activeRepTickets')

                    self.CheckHandlerLog.info("[Reply][%s] Новый ответ.\n %s \n %s \n %s" % (ticket.ticket_id, ticket.email, ticket.subject, ticket.message))
                    self.openbot.sendMessageGroup("[Reply][%s] Новый ответ.\n %s \n %s \n %s" % (ticket.ticket_id, ticket.email, ticket.subject, ticket.message),'HTML', False)

    def checkNewMessage(self):
        tickets = self.getListTickets()
        emailSpamList = Datebase().getSpamEmail().split('\r\n')

        try:
            closedTickets = {k: activeTickets[k] for k  in activeTickets.keys() ^ set(ticket.ticket_id for ticket in tickets)}

            for cTicket in closedTickets:
                self.CheckHandlerLog.info("[%s] закрыт." % cTicket)
                self.openbot.sendMessageGroup("[%s] закрыт." % cTicket)
        except KeyError:
            pass

        tempactiveTickets = {k: activeTickets[k] for k  in activeTickets.keys() & set(ticket.ticket_id for ticket in tickets)}

        activeTickets.clear()

        for i in tempactiveTickets:
            activeTickets[i] = tempactiveTickets[i]

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
                try:
                    account = re.search('Disk quota notification for \“(.+?)\”\.', ticket.message).group(1)
                    quota = re.search('The account currently uses (.+?) of its', ticket.message).group(1)
                    self.CheckHandlerLog.info("[Квота][%s] [%s] %s" % (ticket.ticket_id, account, quota))
                    self.openbot.sendMessageMe("[Квота][%s] [%s] %s" % (ticket.ticket_id, account, quota))
                    Datebase().setTicketClose(ticket.ticket_id)
                except Exception as inst:
                    self.CheckHandlerLog.critical("[DiskUsageWarning] %s" % (inst))
                    self.CheckHandlerLog.critical(sys.exc_info()[0])
                continue
            if re.match(u"\<\!\-\- head not allowed \-\->Домен\: \w{1,25}(-)?(\.)?(\w{1,25})?(\.)?(\w{1,25})?(\.)?\w{1,5}\; Сервер\: http(s)?\:\/\/s\d\.open\.by\:2087\/json\-api\/\; Действие: Успешно заблокирован", ticket.message):
                self.CheckHandlerLog.info("[API block][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[API block][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"\<\!\-\- head not allowed \-\->Домен\: \w{1,25}(-)?(\.)?(\w{1,25})?(\.)?(\w{1,25})?(\.)?\w{1,5}\; Сервер\: http(s)?\:\/\/s\d\.open\.by\:2087\/json\-api\/\; Действие: Успешно разблокирован", ticket.message):
                self.CheckHandlerLog.info("[API unblock][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[API unblock][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"\[s.\.open.by\] Account Terminated:", ticket.subject):
                self.CheckHandlerLog.info("[Удаление][%s] Закрыт" % ticket.ticket_id)
                self.openbot.sendMessageMe("[Удаление][%s] Закрыт" % ticket.ticket_id)
                Datebase().setTicketClose(ticket.ticket_id)
                continue
            if re.match(u"Сведения ИРЦ РУП Белтелеком за", ticket.subject):
                self.CheckHandlerLog.info("[Белтелеком][%s] Задержан" % ticket.ticket_id)
                self.openbot.sendMessageMe("[Белтелеком][%s] Задержан" % ticket.ticket_id)
                Datebase().setTickethold(ticket.ticket_id)
                continue
            if (ticket.client_id == 101373):
                if(self.managerParse(ticket)):
                    continue
            if (ticket.client_id == 94434):
                self.parseDomainbyTask(ticket)
                continue
            if ticket.email in emailSpamList:
                self.CheckHandlerLog.info("[Spam][%s] Перемещен" % ticket.ticket_id)
                self.openbot.sendMessageMe("[Spam][%s] Перемещен" % ticket.ticket_id)
                Datebase().setTicketSpam(ticket.ticket_id)
                continue
            else:
                self.undefinedTicket(ticket)

    def start(self, openbot):
        time.sleep(1)

        self.CheckHandlerLog.info('CheckHandler started.')
        self.openbot = openbot

        loadDataFromServers()
        self.loadCacheActiveTasks()
        self.loadCacheActiveReply()

        while 1:
            try:
                self.checkNewMessage()
                self.checkNewReplies()
                time.sleep(30)
            except Exception as exc:
                self.CheckHandlerLog.critical("[CheckHandler] %s" % exc)
                self.openbot.sendMessageMe("[CheckHandler] %s" % exc)