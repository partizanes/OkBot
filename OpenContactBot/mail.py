
# -*- coding: utf-8 -*-
# by Part!zanes 2017

import smtplib
from threading import Thread
from email.mime.text import MIMEText

from config import Config

def sendMail(_to, _subject, _message):
    thr = Thread(target=send_async_email, args=[_to, _subject, _message])
    thr.start()


def send_async_email(_to, _subject, _message):
    msg = MIMEText('' + _message)
    msg['Subject'] =  "[OpenBot] %s"%(_subject)
    msg['From'] = Config.getMailFrom()

    receivers = _to
    msg['To'] = _to

    s = smtplib.SMTP(Config.getSmtpServer())
    s.sendmail(msg['From'], receivers, msg.as_string())
    s.quit()