# -*- coding: utf-8 -*-
# by Part!zanes 2017

import re,sys,time,telepot,threading
from log import Log
from hdapi import hdapi
from config import Config
from datebase import Datebase
from telepot.loop import MessageLoop
from ticketStatus import HdTicketStatus
from accountloader import getAccountsList
from cpanelapiclient import cpanelApiClient
from hdDepartaments import hdDepartaments as dept
from ticket import activeTickets,activeRepTickets
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton





Config.initializeConfig()
AdminList = Config.getAdminList()
GroupId = Config.getGroupId()
PrivateId = Config.getPrivateId()

class OpenBot(telepot.Bot):
    pass
    botLog = Log('Bot')

    def sendMessageMe(self, msg):
        #len(msg) can throw exception null pointer
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(PrivateId, msg)
        except:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            time.sleep(10)
            return self.sendMessageMe(msg)
    
    def disableButtonByTimeout(self, message):
        try:
            time.sleep(60)
            inline_message_id = (GroupId, message['message_id'])
            self.editMessageReplyMarkup(inline_message_id, reply_markup=None)
        except Exception as exc:
             self.botLog.critical("[Exception] %s" %exc)
             #pass

    def sendMessageGroupInline(self, msg):
        #len(msg) can throw exception null pointer
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Spam', callback_data='Spam'),
                   InlineKeyboardButton(text='Close', callback_data='Close'),
               ]])

            message = self.sendMessage(GroupId, msg, reply_markup=keyboard)

            t10 = threading.Thread(target=self.disableButtonByTimeout, args=(message,))
            t10.start()

        except Exception as exc:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            time.sleep(10)
            return self.sendMessageGroup(msg)

    def sendMessageGroup(self, msg):
        #len(msg) can throw exception null pointer
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(GroupId, msg)
        except:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            time.sleep(10)
            return self.sendMessageGroup(msg)

    def checkAuth(self,id,username):
        try:
            if(AdminList[id] == username): return True
        except Exception:
            return False

    def send(self, username, chat_id, msg, answer):
        self.botLog.info("[%s][%s]Message: %s. Answer: %s"%(username, chat_id, msg, answer))
        #len(msg) can throw exception null pointer
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(chat_id, answer)
        except:
            self.botLog.info("При отправке сообщения прозошла ошибка.Повторная попытка через 10 секунд...")
            time.sleep(10)
            return self.send(username, chat_id, msg, answer)

    def resetCpanelPasswordText(self, domain,  server, username, email):
        return ("""
Сбросить пароль от хостинга %s, вы можете по ссылке:
https://%s:2083/resetpass?start=1

Логин: %s
Почта: %s
                           
Введите имя пользователя и нажмите кнопку "сбросить пароль" , после чего введите адрес контактной почты хостинга и нажмите кнопку "отправить код безопасности". 
Не закрывая данную вкладку , зайдите на почту и скопируйте код безопасности ,после чего вам будет доступно меню ввода нового пароля.
                           
Для входа в панель управления хостингом используйте ссылку:
https://%s.open.by:2083/""" %(domain.encode("utf-8").decode("idna"), server, username, email, server))
    
    def restoreCpanelPassword(self, msg, ticket_id, emailFrom):
        answer = ""
        cpanelUsersAccounts = getAccountsList()

        #Получаем список всех хостинг услуг по адресу контактной почты
        ListOfHostingServices = self.dApi.getListofHostingServices(emailFrom)
        
        if(len(ListOfHostingServices) == 0):
            return "На данный контактный адрес почты не найдено зарегистрированых услуг."

        if(len(ListOfHostingServices) > 0):
            for hostingService in ListOfHostingServices:
                if(cpanelUsersAccounts[hostingService.domain].email not in hostingService.controlemail or cpanelUsersAccounts[hostingService.domain].email != emailFrom):
                    self.botLog.warning('Адрес контактной почты в панели хостинга отличается от панели доменов или от адреса отправителя.')

                    hosting = cpanelUsersAccounts[hostingService.domain].server
                    username = cpanelUsersAccounts[hostingService.domain].username

                    _answer = cpanelApiClient[hosting].call('modifyacct',user=username,contactemail=emailFrom)['result'][0]
            
                    status = int(_answer['status'])
                    message = _answer['statusmsg']

                    self.botLog.debug("[restoreCpanelPassword][modifyacct] %s" %(message))

                    if(status == 1):
                        cpanelUsersAccounts[hostingService.domain].email = emailFrom
                        self.botLog.warning('Контактная почта %s для аккаунта %s синхронизирована с панелью хостинга.' %(emailFrom, hostingService.domain))
                        self.sendMessageGroup('Контактная почта %s для аккаунта %s синхронизирована с панелью хостинга.' %(emailFrom, hostingService.domain))
                    else:
                        self.botLog.debug('Контактная почта в панели хостинга совпадает с панелью доменов.')

                answer += self.resetCpanelPasswordText(hostingService.domain, cpanelUsersAccounts[hostingService.domain].server, cpanelUsersAccounts[hostingService.domain].username, cpanelUsersAccounts[hostingService.domain].email)

            return answer

    def handle(self, msg):
        self.botLog.debug(msg)
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        id, username = msg['from']['id'],msg['from']['username']
        combine = dict(list(activeTickets.items()) + list(activeRepTickets.items()))

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

                if(message[0] == '/'):
                    if(message.split(' ')[0] == '/help'):
                        self.sendMessageGroup("""
/help    - Данное меню.

Следующие команды используються , как ответ(reply) на сообщение:

.move    - Перемещает заявку на менеджеров.

.restore - Генерирует ссылку для сброса пароля.

.spam    - Перемещает заявку в спам с блокировкой отправителя в hd.

.close   - Перемещает заявку в закрытые.
""")
                    return

                try:
                    #Implement accept reply to ticket message 
                    if msg['reply_to_message'] is not None:
                        ticket_id = re.search('\[(Ticket|Reply)]\[(.+?)]', msg['reply_to_message']['text']).group(2)

                        if(ticket_id is None):
                            self.botLog.critical("[handle][group] Не удалось извлечь идентификатор заявки.\n Отладочная информация: \n %s" %(msg))
                            self.sendMessageGroup("[handle][group] Не удалось извлечь идентификатор заявки.\n Отладочная информация: \n %s" %(msg))
                            return

                        if(message[0] == '.'):
                            command = message.split(' ')[0]

                            self.botLog.warning("Получена комманда: %s"%command)

                            if(command == '.restore'):
                                try:
                                    temp = self.restoreCpanelPassword(msg, ticket_id, combine[ticket_id].email)
                                    self.botLog.warning(temp)
                                    self.sendMessageGroup(temp)

                                    #hdapi.postQuickReply(ticket_id, temp , HdTicketStatus.Close, self)
                                except Exception as exc:
                                    self.botLog.critical("[.restore] Во время выполнения возникло исключение: %s" %exc)
                                    self.botLog.critical("[.restore] Stacktrace %s" %(sys.exc_info()[0]))
                                    self.sendMessageGroup("[.restore] Во время выполнения возникло исключение: %s" %exc)
                                return
                            if(command == '.move'):
                                try:
                                    dept_id = dept.DOMAIN
                                    Datebase().moveTicketTo(dept_id.value, ticket_id)
                                    self.botLog.critical("[.move] Заявка %s перемещена в отдел: %s" %(ticket_id, dept_id.name))
                                    self.sendMessageGroup("[.move] Заявка %s перемещена в отдел: %s" %(ticket_id, dept_id.name))
                                except Exception as exc:
                                    self.botLog.critical("[.move] Во время выполнения возникло исключение: %s" %exc)
                                return
                            if(command == '.spam'):
                                inline_message_id = (GroupId, msg['message_id'])
                                spam_email = combine[ticket_id].email  
            
                                Datebase().setSpamEmail(spam_email)
                                Datebase().setTicketSpam(ticket_id)
                                self.deleteMessage(inline_message_id)
                                return
                            if(command == '.close'):
                                inline_message_id = (GroupId, msg['message_id'])
                                Datebase().setTicketClose(ticket_id)
                                self.deleteMessage(inline_message_id)
                                return
 
                        hdapi.postQuickReply(ticket_id, msg['text'] , HdTicketStatus.OPEN, self)

                except Exception as inst:
                    pass
        else:
            self.send(username, chat_id, message,'Вы не авторизованы ¯\_(ツ)_/¯')  

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if msg['message']['text'] is not None:
            ticket_id = re.search('\[(Ticket|Reply)]\[(.+?)]', msg['message']['text']).group(2)

        inline_message_id = (GroupId, msg['message']['message_id'])

        if query_data == 'Spam':
            combine = dict(list(activeTickets.items()) + list(activeRepTickets.items()))
            spam_email = combine[ticket_id].email  
            
            Datebase().setSpamEmail(spam_email)
            Datebase().setTicketSpam(ticket_id)

            self.answerCallbackQuery(query_id, text='Перемещено в спам.Email добавлен в блоклист.')
            self.deleteMessage(inline_message_id)
        elif query_data == 'Close':
            ##self.editMessageReplyMarkup(inline_message_id, reply_markup=None)
            self.deleteMessage(inline_message_id)
            Datebase().setTicketClose(ticket_id)
            self.answerCallbackQuery(query_id, text='Заявка закрыта.')

    def listening(self, dApi):
        time.sleep(3)
        self.dApi = dApi

        self.botLog.info('Bot started.Listening...')

        MessageLoop(self, {'chat': self.handle,
                           'callback_query': self.on_callback_query}).run_as_thread()

        while 1:
            time.sleep(10)