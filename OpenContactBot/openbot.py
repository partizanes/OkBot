# -*- coding: utf-8 -*-
# by Part!zanes 2017

import time
import telepot
from log import Log
from config import Config
from telepot.loop import MessageLoop
from ticket import activeTickets

Config.initializeConfig()
AdminList = Config.getAdminList()
GroupId = Config.getGroupId()
PrivateId = Config.getPrivateId()

class OpenBot(telepot.Bot):
    pass
    botLog = Log('Bot')

    def sendMessageMe(self, msg):
       self.sendMessage(PrivateId, msg)

    def sendMessageGroup(self, msg):
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        self.sendMessage(GroupId, msg)

    def checkAuth(self,id,username):
        try:
            if(AdminList[id] == username): return True
        except Exception:
            return False

    def send(self, username, chat_id, message, answer):
        self.botLog.info("[%s][%s]Message: %s. Answer: %s"%(username, chat_id, message, answer))

        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        self.sendMessage(chat_id, answer)

    def handle(self, msg):
        self.botLog.debug(msg)

        content_type, chat_type, chat_id = telepot.glance(msg)
        id, username, message = msg['from']['id'],msg['from']['username'],msg['text']

        if (content_type, chat_type, chat_id, id, username, message) is None:
            self.botLog.critical("Сообщение не обработано.")
            return

        if(self.checkAuth(id,username)): 
            if(content_type == 'text'):
                self.send(username, chat_id, message, 'Сообщение получено и обработано.')
                #Обработчик сообщения
            else:
                self.send(username, chat_id, '', 'Данный контент не поддерживается.')
        else:
            self.send(username, chat_id, message,'Вы не авторизованы.')

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)

        self.answerCallbackQuery(query_id, text='Принято')

    def listening(self):
        self.botLog.info('Bot started.Listening...\n')
        MessageLoop(self, {'chat': self.handle,
                  'callback_query': self.on_callback_query}).run_as_thread()

        while 1:
            time.sleep(10)


openbot = OpenBot(Config.getToken())