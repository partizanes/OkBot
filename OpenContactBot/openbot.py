# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os,re,sys,time,subprocess,telepot,threading
from log import Log
from hdapi import hdapi
from config import Config
from datebase import Datebase
from accApi import getDataFromApi
from telepot.loop import MessageLoop
from ticket import HdTicketStatus
from accountloader import getAccountsList
from domainapi.domainbyApi import DomainbyApi
from accountloader import loadDataFromServers
from cpanelapiclient import cpanelApiClient
from hdDepartaments import hdDepartaments as dept
from ticket import activeTickets,activeRepTickets
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from domainapi.types.services.serviceStatusTypes import ServiceStatusTypes
from util import Util

Config.initializeConfig()
AdminList = Config.getAdminList()
GroupId = Config.getGroupId()
PrivateIds = Config.getPrivatesId()

class OpenBot(telepot.Bot):
    pass
    botLog = Log('Bot')

    def sendMessageMe(self, msg):
        #len(msg) can throw exception null pointer
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        for private_id in PrivateIds:
            try:
                self.sendMessage(private_id, msg)
            except Exception as exc:
                self.botLog.critical("[sendMessageMe][{0}] {1}".format(private_id, exc))
                self.sendMessageMe("[sendMessageMe][{0}] {1}".format(private_id, exc))
    
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

    def sendMessageGroup(self, msg, parse_mode=None, disable_notification=True):
        #len(msg) can throw exception null pointer
        if(len(msg) > 4096):
            msg = msg[:4096-len(msg)]

        try:
            self.sendMessage(GroupId, msg, parse_mode, True, disable_notification)
        except Exception as exc:
            #if message contain Unsupported values in current parse_mode
            if(exc.error_code == 400 and "Unsupported start tag" in exc.description):
                self.sendMessage(GroupId, msg, None, True, disable_notification)
            else:
                self.botLog.critical("[sendMessageGroup] %s"%(exc))
                self.sendMessageMe("[sendMessageGroup] %s"%(exc))

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
            self.botLog.info("При отправке сообщения произошла ошибка.Повторная попытка через 10 секунд...")
            time.sleep(10)
            return self.send(username, chat_id, msg, answer)

    def resetCpanelPasswordText(self, domain, server, username, email, state):
        return ("""
[Услуга %s]
Сбросить пароль вы можете по ссылке:
https://%s:2083/resetpass?start=1

Логин: %s
Почта: %s
    
        """ %(domain.encode("utf-8").decode("idna"), server, username, email))

    def HostingAccountSuspended(self, domain):
        return ("""
[Услуга %s] на текущий момент приостановлена, восстановление пароля невозможно. 

        """ %(domain.encode("utf-8").decode("idna")))

    def additionalFtpInfo(self):
        return ("""

[Порядок действий]
- введите логин и нажмите кнопку "сбросить пароль"
- введите адрес контактной почты хостинга и нажмите кнопку "отправить код безопасности" 
- не закрывая данную вкладку, зайдите на почту и скопируйте код безопасности, после чего вам будет доступно меню ввода нового пароля.

[Авторизация]
Для входа в панель управления хостингом используйте ссылку:
https://cpanel.domain.by

[FTP]
Как настроить FTP-клиент: https://domain.by/info-help/cpanel/#question_10
""")

    def accessToFtp(self, domain, server, state):
        return ("""
Для доступа к %s(%s) по протоколу FTP используйте имя пользователя и пароль такие же, как и для доступа в cPanel.

хост: %s или %s (если домен не делегирован на сервера domain.by)
порт: 21

Подробная информация по настройке FTP: https://domain.by/info-help/cpanel/#question_10

        """ %(domain.encode("utf-8").decode("idna"), state, domain.encode("utf-8").decode("idna"), server))

    def accessToSsh(self, domain, server, username, state):
        return ("""
Для доступа к %s(%s) используйте имя пользователя и пароль, как в панели управления хостингом.

Хост:      %s или %s
Порт:      20022
Логин:     %s

        """ %(domain.encode("utf-8").decode("idna"), state, domain.encode("utf-8").decode("idna"), server, username))
    
    def changeContactEmailInCpanel(self, emailFrom, domainName, cpanelUsersAccounts):
        self.botLog.warning('Адрес контактной почты в панели хостинга отличается от панели доменов или от адреса отправителя.')

        hosting = cpanelUsersAccounts[domainName].server
        username = cpanelUsersAccounts[domainName].username

        _answer = cpanelApiClient[hosting].call('modifyacct',user=username,contactemail=emailFrom)['result'][0]
            
        status = int(_answer['status'])
        message = _answer['statusmsg']

        self.botLog.debug("[restoreCpanelPassword][modifyacct] %s" %(message))

        if(status == 1):
            cpanelUsersAccounts[domainName].email = emailFrom
            self.botLog.warning('Контактная почта %s для аккаунта %s синхронизирована с панелью хостинга.' %(emailFrom, domainName))
            self.sendMessageGroup('Контактная почта %s для аккаунта %s синхронизирована с панелью хостинга.' %(emailFrom, domainName))

    def restoreCpanelPassword(self, emailFrom):
        answer = ""
        cpanelUsersAccounts = getAccountsList()

        ListOfHostingServices  = DomainbyApi.getListofHostingServices(emailFrom)
        
        if not len(ListOfHostingServices):
            return "На данный контактный адрес почты не найдено зарегистрированных услуг. Заявка на восстановление доступа должна быть отправлена с контакного адреса хостинга."

        suspended = False

        for hosting in ListOfHostingServices:
            domainName = hosting["DomainName"]

            if(cpanelUsersAccounts[domainName].email not in hosting["AllEmails"] or cpanelUsersAccounts[domainName].email != emailFrom):
                self.changeContactEmailInCpanel(emailFrom, domainName, cpanelUsersAccounts)
            else:
                self.botLog.debug('Контактная почта в панели хостинга совпадает с панелью доменов.')

            if(hosting["ServiceStatus"] == ServiceStatusTypes.OK.name):
                answer += self.resetCpanelPasswordText(domainName, cpanelUsersAccounts[domainName].server, cpanelUsersAccounts[domainName].username, cpanelUsersAccounts[domainName].email, hosting["ServiceStatus"])
            else:
                suspended = True
                answer += self.HostingAccountSuspended(domainName)


        if (len(ListOfHostingServices) == 1 and not suspended) or len(ListOfHostingServices) > 1:
            answer += self.additionalFtpInfo()

        return answer

    def howToConnectFtp(self, emailFrom):
        answer = ""
        cpanelUsersAccounts = getAccountsList()

        # Получаем список всех хостинг услуг по адресу контактной почты
        ListOfHostingServices  = DomainbyApi.getListofHostingServices(emailFrom)
        
        if not len(ListOfHostingServices):
            return "Подробная информация по настройке FTP: https://domain.by/info-help/cpanel/#question_10"

        for hosting in ListOfHostingServices:

            domainName = hosting["DomainName"]

            if(cpanelUsersAccounts[domainName].email not in hosting["AllEmails"] or cpanelUsersAccounts[domainName].email != emailFrom):
                self.changeContactEmailInCpanel(emailFrom, domainName, cpanelUsersAccounts)
            else:
                self.botLog.debug('Контактная почта в панели хостинга совпадает с панелью доменов.')

            answer += self.accessToFtp(domainName, cpanelUsersAccounts[domainName].server, hosting["ServiceStatus"])

        return answer

    def grantAccessToSsh(self, emailFrom):
        answer = ""
        cpanelUsersAccounts = getAccountsList()

        # Получаем список всех хостинг услуг по адресу контактной почты
        ListOfHostingServices  = DomainbyApi.getListofHostingServices(emailFrom)

        if not len(ListOfHostingServices):
            return "На данный контактный адрес почты не найдено зарегистрированных услуг.\n Заявка должна быть оформлена с контактного адреса почты хостинга."

        for hostingService in ListOfHostingServices:
            try:
                domainName = hostingService["DomainName"]
                server = cpanelUsersAccounts[domainName].server
                username = cpanelUsersAccounts[domainName].username
                package = cpanelUsersAccounts[domainName].package

                if("xS" in package):
                    answer = "Для аккаунта хостинга %s отсутствует возможность доступа по SSH:\n https://domain.by/info-help/hosting/#question_12 \n\n"%(domainName)
                    continue

                # TODO CHECK IT
                if(cpanelUsersAccounts[domainName].email not in hostingService["AllEmails"] or cpanelUsersAccounts[domainName].email != emailFrom):
                    self.changeContactEmailInCpanel(emailFrom, domainName, cpanelUsersAccounts)
                else:
                    self.botLog.debug('Контактная почта в панели хостинга совпадает с панелью доменов.')
            
                output = cpanelApiClient[server].call_v1('modifyacct',user=username,HASSHELL=1)
                answer += "Произведена активация ssh доступа для %s:\n"%(domainName)
                self.botLog.debug(output)

                answer += self.accessToSsh(domainName, server, username, hostingService["ServiceStatus"])
            except KeyError:
                self.botLog.error("Аккаунт хостинга не обнаружен на серверах: %s"%domainName)
                self.sendMessageGroup("Аккаунт хостинга не обнаружен на серверах: %s"%domainName)

        return answer

    def getServerbyEmail(self, _domain):
        cpanelUsersAccounts = getAccountsList()

        self.botLog.info("[getServerbyEmail] Производится поиск домена %s на хостинге..."%_domain)

        for key, capi in cpanelApiClient.items():
            _local = capi.call('domainuserdata',domain=_domain)
            _status = int(_local['result'][0]['status'])

            if(_status == 1):
                return key
        return None

    def suspendOutgoingEmail(self, message):
        cpanelUsersAccounts = getAccountsList()

        if(len(message.split(' ')) < 2):
            self.botLog.critical("[/suspendOutgoingEmail] Email не указан.")
            self.sendMessageGroup("[/suspendOutgoingEmail] Email не указан.")
            return

        _email = message.split(' ')[1]

        if(_email == "" or '@' not in _email):
            self.botLog.critical("[/suspendOutgoingEmail] Email указан неверно.")
            self.sendMessageGroup("[/suspendOutgoingEmail] Email указан неверно.")
            return

        _domain = _email.split('@')[1]
        _hosting = self.getServerbyEmail(_domain)

        if(_hosting is None):
            self.botLog.info("[/suspendOutgoingEmail] Аккаунт хостинга не найден : %s" %_email)
            self.sendMessageGroup("[/suspendOutgoingEmail] Аккаунт хостинга не найден : %s" %_email)
            return

        _username = cpanelApiClient[_hosting].call_v1('domainuserdata', domain=_domain)['data']['userdata']['user']
        self.botLog.debug("[/suspendOutgoingEmail] Имя пользователя: %s" %_username)

        _answer = cpanelApiClient[_hosting].call_v1('suspend_outgoing_email', user=_username)
        _status = int(_answer['metadata']['result'])

        if(_status == 1):
            self.botLog.info("Возможность отправки почты для: %s заблокирована. Сервер: %s"%(_username, _hosting))
            self.sendMessageGroup("Возможность отправки почты для: %s заблокирована. Сервер: %s"%(_username, _hosting))
            return

        self.botLog.critical("[/suspendOutgoingEmail] Ошибка блокировки: %s"%(_message))
        self.sendMessageGroup("[/suspendOutgoingEmail] Ошибка блокировки: %s"%(_message))

    def unSuspendOutgoingEmail(self, message):
        cpanelUsersAccounts = getAccountsList()

        if(len(message.split(' ')) < 2):
            self.botLog.critical("[/unSuspendOutgoingEmail] Email не указан.")
            self.sendMessageGroup("[/unSuspendOutgoingEmail] Email не указан.")
            return

        _email = message.split(' ')[1]

        if(_email == "" or '@' not in _email):
            self.botLog.critical("[/unSuspendOutgoingEmail] Email указан неверно.")
            self.sendMessageGroup("[/unSuspendOutgoingEmail] Email указан неверно.")
            return

        _domain = _email.split('@')[1]
        _hosting = self.getServerbyEmail(_domain)

        if(_hosting is None):
            self.botLog.info("[/unSuspendOutgoingEmail] Аккаунт хостинга не найден : %s" %_email)
            self.sendMessageGroup("[/unSuspendOutgoingEmail] Аккаунт хостинга не найден : %s" %_email)
            return

        _username = cpanelApiClient[_hosting].call_v1('domainuserdata', domain=_domain)['data']['userdata']['user']
        self.botLog.debug("[/unSuspendOutgoingEmail] Имя пользователя: %s" %_username)

        _answer = cpanelApiClient[_hosting].call_v1('unsuspend_outgoing_email', user=_username)
        _status = int(_answer['metadata']['result'])

        if(_status == 1):
            self.botLog.info("Возможность отправки почты для: %s разблокирована. Сервер: %s"%(_username, _hosting))
            self.sendMessageGroup("Возможность отправки почты для: %s разблокирована. Сервер: %s"%(_username, _hosting))
            return

        self.botLog.critical("[/unSuspendOutgoingEmail] Ошибка разблокировки: %s"%(_message))
        self.sendMessageGroup("[/unSuspendOutgoingEmail] Ошибка разблокировки: %s"%(_message))


    def unBlockEmail(self, message):
        cpanelUsersAccounts = getAccountsList()

        if(len(message.split(' ')) < 2):
            self.botLog.critical("[/unblockmail] Email не указан.")
            self.sendMessageGroup("[/unblockmail] Email не указан.")
            return

        _email = message.split(' ')[1]

        if(_email == "" or '@' not in _email):
            self.botLog.critical("[/unblockmail] Email указан неверно.")
            self.sendMessageGroup("[/unblockmail] Email указан неверно.")
            return

        _domain = _email.split('@')[1]
        _hosting = self.getServerbyEmail(_domain)

        if(_hosting is None):
            self.botLog.info("[/unblockmail] Аккаунт хостинга не найден : %s" %_email)
            self.sendMessageGroup("[/unblockmail] Аккаунт хостинга не найден : %s" %_email)
            return

        _username = cpanelApiClient[_hosting].call_v1('domainuserdata', domain=_domain)['data']['userdata']['user']
        self.botLog.debug("[/unblockmail] Имя пользователя: %s" %_username)

        _answer = (cpanelApiClient[_hosting].uapi('Email','unsuspend_login', user=_username, email=_email))
        _status = int(_answer['result']['status'])
        _message = _answer['result']['messages']

        if(_status == 1):
            self.botLog.info("Возможность входа для почтового аккаунта: %s разблокирована. Аккаунт хостинга: %s. Сервер: %s"%(_email, _username, _hosting))
            self.sendMessageGroup("Возможность входа для почтового аккаунта: %s разблокирована. Аккаунт хостинга: %s. Сервер: %s"%(_email, _username, _hosting))
            return

        self.botLog.critical("[/blockmail] Ошибка блокировки: %s"%(_message))
        self.sendMessageGroup("[/blockmail] Ошибка блокировки: %s"%(_message))

    def blockByEmail(self, message):
        cpanelUsersAccounts = getAccountsList()

        if(len(message.split(' ')) < 2):
            self.botLog.critical("[/blockmail] Email не указан.")
            self.sendMessageGroup("[/blockmail] Email не указан.")
            return

        _email = message.split(' ')[1]

        if(_email == "" or '@' not in _email):
            self.botLog.critical("[/blockmail] Email не указан или указан неверно.")
            self.sendMessageGroup("[/blockmail] Email не указан или указан неверно.")
            return

        _domain = _email.split('@')[1]
        _hosting = self.getServerbyEmail(_domain)

        if(_hosting is None):
            self.botLog.info("[/blockmail] Аккаунт хостинга не найден : %s" %_email)
            self.sendMessageGroup("[/blockmail] Аккаунт хостинга не найден : %s" %_email)
            return

        _username = cpanelApiClient[_hosting].call_v1('domainuserdata',domain=_domain)['data']['userdata']['user']
        self.botLog.debug("[/blockmail] Имя пользователя: %s" %_username)

        _answer = (cpanelApiClient[_hosting].uapi('Email','suspend_login',user=_username,email=_email))
        _status = int(_answer['result']['status'])
        _message = _answer['result']['messages']

        if(_status == 1):
            self.botLog.info("Возможность входа для почтового аккаунта: %s заблокирована. Аккаунт хостинга: %s. Сервер: %s"%(_email, _username, _hosting))
            self.sendMessageGroup("Возможность входа для почтового аккаунта: %s заблокирована. Аккаунт хостинга: %s. Сервер: %s"%(_email, _username, _hosting))
            return

        self.botLog.critical("[/blockmail] Ошибка блокировки: %s"%(_message))
        self.sendMessageGroup("[/blockmail] Ошибка блокировки: %s"%(_message))

    def handle(self, msg):
        self.botLog.debug(msg)
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        id, username = msg['from']['id'],msg['from']['username']
        #combine = dict(list(activeTickets.items()) + list(activeRepTickets.items()))

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

                # Replace double spaces and cleanup
                message = ' '.join(message.strip().split())

                if(message[0] == '/'):

                    if(len(message.split(' ')) > 1):
                        checkCmd = message.split(' ')[0]
                    else:
                        checkCmd = message

                    self.botLog.warning("Получена комманда: %s"%checkCmd)

                    if(checkCmd == '/help'):
                        self.sendMessageGroup("""
/help     - Данное меню.
/update   - Проверка наличия обновлений.
/fupdate  - Принудительное обновление.
/version  - Отображает версию ядра.
/uptime   - Отображает время с момента запуска.
/exclude  - Добавляет или удаляет доменное имя в список исключений. (/exclude domain.by)
/cpreload - Принудительно загружает список аккаунтов из cpanel.
/bemail   - Блокировка авторизации для почтового аккаунта (/blockemail)
/unemail  - Разблокировка авторизации для почтового аккаунта (/unblockemail)
/restore  - Функция для тестирования ответа сервера (/restore email)
/smail    - Блокировка возможности отправки исходящей почты для аккаунта (/suspendemail email)
/unsmail  - Разблокировка возможности отправки исходящей почты для аккаунта (/unsuspendemail email)
/session  - Генерирует одноразовую ссылку для авторизации в cpanel пользователя (/session domain.by)

Следующие команды используются , как ответ(reply) на сообщение:

.move    - Перемещает заявку на менеджеров.

.restore - Генерирует ссылку для сброса пароля.

.spam    - Перемещает заявку в спам с блокировкой отправителя в hd.

.close   - Перемещает заявку в закрытые.

.exclude - Добавляет или удаляет доменное имя в список исключений. Пример: .exclude domain.by

.ssh     - Добавляет пользователю возможность подключения по ssh.

.ftp     - Предоставляет информацию по подключению к FTP.
""")
                        return
                    if (checkCmd == '/restore'):
                        subcommand = message.split()[1]
                        self.sendMessageGroup('[/restore]%s'%(self.restoreCpanelPassword(subcommand)))
                        return
                    if (checkCmd == '/ssh'):
                        subcommand = message.split()[1]
                        self.sendMessageGroup('[/ssh]%s'%(self.grantAccessToSsh(subcommand)))
                        return
                    if (checkCmd == '/update'):
                        self.sendMessageGroup("Проводим проверку наличия обновлений...")
                        Util.checkUpdate(self.botLog, self)
                        return
                    if (checkCmd == '/fupdate'):
                        self.sendMessageGroup("Производим принудительное обновление...")
                        Util.checkUpdate(self.botLog, self, True)
                        return
                    if (checkCmd == '/version'):
                        self.sendMessageGroup('Текущая версия: %s \nВерсия на сервере: %s'%(Util.getCurrentVersion(), Util.getVersionAtServer()))
                        return
                    if (checkCmd == '/uptime'):
                        self.sendMessageGroup('Время работы: %s'%(Util.getUpime()))
                        return
                    if (checkCmd == '/cpreload'):
                        self.sendMessageGroup('Принудительная загрузка хостинг аккаунтов.')
                        loadDataFromServers(True)
                        self.sendMessageGroup("...Завершено.Найдено %s аккаунтов." %(len(getAccountsList())))
                        self.botLog.info("...Загружено %s аккаунтов." %(len(getAccountsList())))
                        return 
                    if (checkCmd == '/exclude'):

                        if(len(message.split(' ')) > 1):
                            subcommand = message.split(' ')[1]
                        else:
                            self.botLog.critical("[/exclude] Имя домена не указано.")
                            self.sendMessageGroup("Имя домена не указано. Cписок исключений: %s" %(",".join(Config.getExcludeDomainList())))
                            return

                        tempExcludeList = Config.getExcludeDomainList()

                        if(subcommand in tempExcludeList):
                            tempExcludeList.remove(subcommand)
                        else:
                            tempExcludeList.append(subcommand)

                        Config.setConfigValue('exclude', 'create', ",".join(tempExcludeList))
                        Config.saveConfig()

                        self.sendMessageGroup("[.exclude] Сохранен список исключений: %s" %(",".join(tempExcludeList)))
                        return
                    if(checkCmd in ['/bemail','/blockemail']):
                        self.blockByEmail(message)
                        return
                    if(checkCmd in ['/unemail','/unblockemail']):
                        self.unBlockEmail(message)
                        return
                    if(checkCmd in ['/smail','/suspendemail']):
                        self.suspendOutgoingEmail(message)
                        return
                    if(checkCmd in ['/unsmail','unsuspendemail']):
                        self.unSuspendOutgoingEmail(message)
                        return
                    if(checkCmd == '/session'):

                        if(len(message.split(' ')) > 1):
                            subcommand = message.split(' ')[1]
                        else:
                            self.botLog.critical("[/session] Имя домена не указано.")
                            self.sendMessageGroup("Имя домена не указано.")
                            return

                        try:
                            answer = getDataFromApi('/api/session/{0}'.format(subcommand))

                            _str = ""

                            for server in answer:
                                _str += "".join("[{0}] \n Cсылка: {1} \n\n".format(server, answer[server]['url']))

                            self.sendMessageGroup(_str)

                        except Exception as exc:
                            self.botLog.critical("[/session] Во время выполнения возникло исключение: %s" %repr(exc))
                            self.sendMessageGroup("[/session] Во время выполнения возникло исключение: %s" %repr(exc))
                       
                        return

                    self.botLog.critical("[command] Команда не обработана: %s" %checkCmd)
                    self.sendMessageGroup("[command] Команда не обработана: %s" %checkCmd)

                    return
                try:
                    #Implement accept reply to ticket message 
                    if msg['reply_to_message'] is not None:

                        #The don`t ticket`s reply
                        if(re.search('\[(Ticket|Reply)]\[(.+?)]', msg['reply_to_message']['text']) is None):
                            self.botLog.error("[handle][NOT_ERROR] Не удалось извлечь идентификатор заявки.\n")
                            return

                        ticket_id = re.search('\[(Ticket|Reply)]\[(.+?)]', msg['reply_to_message']['text']).group(2)
                        original_message_id = (GroupId, msg['reply_to_message']['message_id'])
                        ticket_email = Datebase().getEmailByTicketId(ticket_id)

                        if(message[0] == '.'):
                            command = message.split(' ')[0]

                            self.botLog.warning("Получена комманда: %s"%command)

                            if(command == '.restore'):
                                try:
                                    reset_answer = self.restoreCpanelPassword(ticket_email)
                                    trueAnswer = ['не найдено зарегистрированных услуг', 'Сбросить пароль вы можете по ссылке']

                                    self.botLog.warning(reset_answer)

                                    if any(x in reset_answer for x in trueAnswer):
                                        hdapi.postQuickReply(ticket_id, reset_answer, HdTicketStatus.CLOSED, self)
                                    else:
                                        self.sendMessageGroup(reset_answer)

                                except Exception as exc:
                                    self.botLog.critical("[.restore] Во время выполнения возникло исключение: %s" %repr(exc))
                                    self.sendMessageGroup("[.restore] Во время выполнения возникло исключение: %s" %repr(exc))
                                return

                            if(command == '.move'):
                                try:
                                    dept_id = dept.DOMAIN
                                    Datebase().moveTicketTo(dept_id.value, ticket_id)
                                    self.deleteMessage(original_message_id)
                                    self.botLog.critical("[.move] Заявка %s перемещена в отдел: %s" %(ticket_id, dept_id.name))
                                    self.sendMessageGroup("[.move] Заявка %s перемещена в отдел: %s" %(ticket_id, dept_id.name))
                                except Exception as exc:
                                    self.botLog.critical("[.move] Во время выполнения возникло исключение: %s" %repr(exc))
                                return

                            if(command == '.spam'):
                                spam_email = ticket_email
            
                                Datebase().setSpamEmail(spam_email)
                                Datebase().setTicketSpam(ticket_id)
                                self.deleteMessage(original_message_id)
                                return

                            if(command == '.ssh'):
                                try:
                                    reset_answer = self.grantAccessToSsh(ticket_email)
                                    trueAnswer = ['не найдено зарегистрированных услуг', 'как в панели управления хостингом', 'отсутствует возможность доступа', ]

                                    self.botLog.warning(reset_answer)
                                    
                                    if any(x in reset_answer for x in trueAnswer):
                                        hdapi.postQuickReply(ticket_id, reset_answer, HdTicketStatus.CLOSED, self)
                                    else:
                                        self.sendMessageGroup(reset_answer)
                                except Exception as exc:
                                    self.botLog.critical("[.ssh] Во время выполнения возникло исключение: %s" %repr(exc))
                                    self.sendMessageGroup("[.ssh] Во время выполнения возникло исключение: %s" %repr(exc))
                                return

                            if(command == '.ftp'):
                                try:
                                    reset_answer = self.howToConnectFtp(ticket_email)
                                    trueAnswer = ['Подробная информация по настройке FTP', 'как и для доступа в cPanel']

                                    self.botLog.warning(reset_answer)
                                    
                                    if any(x in reset_answer for x in trueAnswer):
                                        hdapi.postQuickReply(ticket_id, reset_answer, HdTicketStatus.CLOSED, self)
                                    else:
                                        self.sendMessageGroup(reset_answer)
                                except Exception as exc:
                                    self.botLog.critical("[.ftp] Во время выполнения возникло исключение: %s" %repr(exc))
                                    self.sendMessageGroup("[.ftp] Во время выполнения возникло исключение: %s" %repr(exc))
                                return

                            if(command == '.close'):
                                Datebase().setTicketClose(ticket_id)
                                self.deleteMessage(original_message_id)
                                return

                            if(command == '.exclude'):
                                subcommand = message.split(' ')[1]

                                if(subcommand is None or subcommand == ""):
                                    self.botLog.critical("[.exclude] Имя домена не указано.")
                                    return

                                tempExcludeList = Config.getExcludeDomainList()

                                if(subcommand in tempExcludeList):
                                    self.deleteMessage(original_message_id)
                                    tempExcludeList.remove(subcommand)
                                else:
                                    tempExcludeList.append(subcommand)

                                Config.setConfigValue('exclude', 'create', ",".join(tempExcludeList))
                                Config.saveConfig()
                                
                                Datebase().setTicketClose(ticket_id)
                                self.deleteMessage(original_message_id)

                                self.sendMessageGroup("[.exclude] Сохранен список исключений: %s" %(",".join(tempExcludeList)))
                                return

                            self.botLog.critical("[command] Команда не обработана: %s" %command)
                            self.sendMessageGroup("[command] Команда не обработана: %s" %command)
                            return

                        hdapi.postQuickReply(ticket_id, msg['text'] , HdTicketStatus.OPEN, self)

                except Exception as exc:
                    self.botLog.debug("[Exception][handle] %s" %repr(exc))
                    self.sendMessageMe("[Exception][handle] %s" %repr(exc))
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
        time.sleep(5)
        self.dApi = dApi

        self.botLog.info('Bot started.Listening...')

        try:
            MessageLoop(self, {'chat': self.handle,
                               'callback_query': self.on_callback_query}).run_as_thread()
        except Exception as exc:
             self.botLog.critical("[MessageLoop][critical] %s" %(exc))


        while 1:
            time.sleep(10)