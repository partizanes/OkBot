# -*- coding: utf-8 -*-
# by Part!zanes 2017

from log import Log
from time import sleep
from cpanelapiclient import cpanelApiClient

class cpanelServerHandler(object):
    avgMax = {
        's2.open.by' : 10.0,
        's3.open.by' : 10.0,
        's4.open.by' : 10.0,
        's5.open.by' : 10.0,
        's6.open.by' : 15.0,
        's7.open.by' : 10.0
         }

    sendNotify = {
        's2.open.by' : False,
        's3.open.by' : False,
        's4.open.by' : False,
        's5.open.by' : False,
        's6.open.by' : False,
        's7.open.by' : False
        }

    def checkLoadAvg(self):
         for key, client in cpanelApiClient.items():
             try:
                answer = client.call_v1('loadavg')

                #one = float(answer['one'])
                five = float(answer['five'])
                #fifteen = float(answer['fifteen'])

                if(five > self.avgMax[key] and self.sendNotify[key] == False):
                    self.sendNotify[key] = True
                    self.csLog.critical("[%s] LoadAverage: %s" %(key, five))
                    self.openbot.sendMessageGroup("[%s] LoadAverage: %s" %(key, five))
                elif(five < self.avgMax[key] and self.sendNotify[key] == True):
                    self.sendNotify[key] = False

             except Exception as exc:
                self.csLog.critical("[checkLoadAvg]: %s" %exc.args)
                self.openbot.sendMessageMe("[checkLoadAvg]: %s" %exc.args)

    def start(self,openbot):
        self.openbot = openbot
        self.csLog = Log("cServHandler")

        while 1:
            self.checkLoadAvg()
            sleep(300)

