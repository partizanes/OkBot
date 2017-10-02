# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re
import requests
from log import Log
from config import Config as cfg

class hdapi(object):
    cfg.initializeConfig()
    hdLog = Log("hdLog")
    hdUrl = cfg.getHdUrl()

    @staticmethod
    def postQuickReply(ticket_id, reply, status, openbot):
        secretKey = requests.get(cfg.getHdBotToken(), auth=requests.auth.HTTPBasicAuth(cfg.getHdBotUsername(), cfg.getHdBotPassword())).text

        if(secretKey is None):
                hdapi.hdLog.critical("[postQuickReply] Не удалось получить secretKey")
                openbot.sendMessageGroup("[postQuickReply] Не удалось получить secretKey")

        cookies = dict(staff_data=secretKey,supportadmin=cfg.getHdSession())

        r = requests.get(hdapi.hdUrl + '/ticket_detail.php?ticket_id=%s' % (ticket_id), cookies=cookies)
        subject = re.search(u'Предмет\n\t\t</td>\n\t\t<td class=\"ticket-content-[a-z]{1,10}\" colspan=5>\n\n\t\t(.+?)\n\n\t\t</td>', r.text).group(1).replace('\r','').replace('\t','')

        if subject is None:
            hdapi.hdLog.critical("[postQuickReply] Не удалось получить тему для ответа")
            openbot.sendMessageGroup("[postQuickReply] Не удалось получить тему для ответа")
            subject = "Ответ на заявку %s" % (ticket_id)

        dataToPost = {
            'ticket_id': ticket_id,
            'subject': subject,
            'reply': reply,
            'act':'quickreply',
            'submit':'Послать ответ',
            'dotktaction': status, 
            'canned':'0'
           }

        r = requests.post(hdapi.hdUrl + '/ticket_detail.php?ticket_id=%s' % (ticket_id), data = dataToPost, cookies=cookies)

        if(r.status_code == 200):
            hdapi.hdLog.info("[postQuickReply][%s] Ответ отправлен." % (ticket_id))
            openbot.sendMessageGroup("[%s] Ответ отправлен." % (ticket_id))
            return True
        else:
            hdapi.hdLog.critical("[postQuickReply][%s] Попытка ответа неудачна.Код ответа: %s" % (ticket_id, r.status_code))
            openbot.sendMessageGroup("[postQuickReply][%s] Попытка ответа неудачна.Код ответа: %s" % (ticket_id, r.status_code))
            return False