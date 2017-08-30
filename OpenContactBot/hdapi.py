# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re
import requests
from log import Log
from config import Config as cfg
from ticketStatus import HdTicketStatus
from openbot import openbot

class hdapi(object):
    hdLog = Log("hdLog")
    openbot = openbot
    hdUrl = cfg.getHdUrl()

    @staticmethod
    def getAuthCookie():
        try:
            response = requests.get(cfg.getHdBotToken(), auth=requests.auth.HTTPBasicAuth(cfg.getHdBotUsername(), cfg.getHdBotPassword()))
            return response.text
        except requests.exceptions.RequestException as e:
            hdapi.hdLog.critical("[getAuthCookie] %s" %(e))
            hdapi.openbot.sendMessageMe("[getAuthCookie] %s" %(e))

    @staticmethod
    def postQuickReply(ticket_id, reply, status):
        secretKey = hdapi.getAuthCookie()

        if(secretKey is None):
            hdapi.hdLog.info("[postQuickReply] Не удалось получить secretKey")
            hdapi.openbot.sendMessageMe("[postQuickReply] Не удалось получить secretKey")
            return 
            #TODO Implement task handler

        cookies = dict(staff_data=secretKey,supportadmin=cfg.getHdSession())

        r = requests.get(hdapi.hdUrl + '/ticket_detail.php?ticket_id=%s' %(ticket_id), cookies=cookies)
        subject = re.search(u'Предмет\n\t\t</td>\n\t\t<td class=\"ticket-content-[a-z]{1,10}\" colspan=5>\n\n\t\t(.+?)\n\n\t\t</td>', r.text).group(1).replace('\r','').replace('\t','')

        if subject is None:
            hdapi.hdLog.critical("[postQuickReply] Не удалось получить тему для ответа")
            hdapi.openbot.sendMessageMe("[postQuickReply] Не удалось получить тему для ответа")
            subject = "Ответ на заявку %s" %(ticket_id)

        dataToPost = {
            'ticket_id': ticket_id,
            'subject': subject,
            'reply': reply,
            'act':'quickreply',
            #'bccaddress':'',
            'submit':'Послать ответ',
            #'ccaddress':'', 
            'dotktaction': status, 
            #'reply_minutes':'', 
            'canned':'0'
           }

        r = requests.post(hdapi.hdUrl + '/ticket_detail.php?ticket_id=%s' %(ticket_id), data = dataToPost, cookies=cookies)

        if(r.status_code == 200):
            hdapi.hdLog.info("[postQuickReply][%s] Ответ отправлен." %(ticket_id))
            hdapi.openbot.sendMessageMe("[postQuickReply][%s]  Ответ отправлен." %(ticket_id))
            return True
        else:
            hdapi.hdLog.critical("[postQuickReply][%s] Попытка ответа неудачна.Код ответа: %s" %(ticket_id, r.status_code))
            hdapi.openbot.sendMessageMe("[postQuickReply][%s] Попытка ответа неудачна.Код ответа: %s" %(ticket_id, r.status_code))
            return False


