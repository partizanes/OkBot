# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re
import time
import telepot
from log import Log
from config import Config
from telepot.loop import MessageLoop
from ticket import activeTickets
from ticketStatus import HdTicketStatus
from hdapi import hdapi

Config.initializeConfig()
AdminList = Config.getAdminList()
GroupId = Config.getGroupId()
PrivateId = Config.getPrivateId()

class OpenBot(telepot.Bot):
    pass
    botLog = Log('Bot')

    def sendMessageMe(self, msg):
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(PrivateId, msg)
        except:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            sleep(10)
            return self.sendMessageMe(msg)

    def sendMessageGroup(self, msg):
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(GroupId, msg)
        except:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            sleep(10)
            return self.sendMessageGroup(msg)

    def checkAuth(self,id,username):
        try:
            if(AdminList[id] == username): return True
        except Exception:
            return False

    def send(self, username, chat_id, msg, answer):
        self.botLog.info("[%s][%s]Message: %s. Answer: %s"%(username, chat_id, msg, answer))

        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(chat_id, answer)
        except:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            sleep(10)
            return self.send(username, chat_id, msg, answer)
        

    def handle(self, msg):
        self.botLog.debug(msg)
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        id, username = msg['from']['id'],msg['from']['username']

        if (content_type, chat_type, chat_id, id, username) is None:
            self.botLog.critical("Сообщение не обработано.")
            return

        if(content_type != 'text'):
            self.send(username, chat_id, '', '[NOT IMPLEMENTED] Данный контент не поддерживается.')
            return

        message = msg['text']

        if(self.checkAuth(id,username)):
            if(chat_type == 'private'):
                main_keyboard = [['Домены', 'Хостинг' ], ['Другое', 'Выход']]
                sub_keyboard = [['Sub option #1_1', 'Sub option #1_2'], ['Sub option #1_3', 'Sub option #1_4'],['Back to Main menu']]
                
                if message =='/start':
                    self.sendMessage(chat_id, '.', reply_markup={'keyboard': main_keyboard, 'resize_keyboard': True})
                elif message in [j for i in main_keyboard for j in i]:

                     if message == 'Домены':
                         sub_buttons = {'keyboard': sub_keyboard}
                         self.sendMessage(chat_id, '.', reply_markup=sub_buttons)
                     elif message == 'Выход':
                         self.sendMessage(chat_id, ".", reply_markup={'remove_keyboard': True})


                elif message in [j for i in sub_keyboard for j in i]:
                        # an option from Sub keyboard is chosen:
                        if message == 'Sub option #1_1':
                            self.sendMessage(chat_id, 'Sub selected %s' %message)
                        if message == 'Back to Main menu':
                            self.sendMessage(chat_id, 'Main options', reply_markup={'keyboard': main_keyboard})
                else:
                    self.sendMessage(chat_id, 'Invalid Message. please select an option from keyboard')
            elif(chat_type == 'group'):
                
                try:
                    #Implement accept reply to ticket message 
                    if msg['reply_to_message'] is not None:
                        ticket_id = re.search('\[(Ticket|Reply)]\[(.+?)]', msg['reply_to_message']['text']).group(2)

                        if(ticket_id is None):
                            self.botLog.critical("[handle][group] Не удалось извлечь идентификатор заявки.\n Отладочная информация: \n %s" %(msg))
                            self.sendMessageGroup("[handle][group] Не удалось извлечь идентификатор заявки.\n Отладочная информация: \n %s" %(msg))
                            return

                        hdapi.postQuickReply(ticket_id, msg['text'] , HdTicketStatus.OPEN, openbot)

                except Exception as inst:
                    pass
        else:
            self.send(username, chat_id, message,'Вы не авторизованы ¯\_(ツ)_/¯')  
            
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