# -*- coding: utf-8 -*-
# by Part!zanes 2017

import os, sys, time, git, subprocess
import urllib.request
from datetime import datetime

startTime = datetime.now()

class Util(object):

    @staticmethod
    def get_script_path():
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    @staticmethod
    def createDir(patch):
        if not os.path.exists(patch):
            os.makedirs(patch)

    @staticmethod
    def getFileChangeTime(patch):
        return os.path.getmtime(patch)
    
    @staticmethod
    def fileExits(filePath):
        return os.path.exists(filePath)
    
    @staticmethod
    def patchJoin(patch,*patchs):
        return(os.path.join(patch,*patchs))

    @staticmethod
    def checkUpdate(coreLog, openbot, sendmessage=True):
        if(Util.needUpdate()):
            openbot.sendMessageGroup('Обнаружено обновление...')
           
            curPath = os.getcwd()

            if (os.name == 'nt'):
                splitedPath = curPath.split("\\")[0:-1]
            else:
                splitedPath = curPath.split('/')[0:-1]

            if (os.name == 'nt'):
                gitDirPath = "\\".join(map(str,splitedPath))
            else:
                gitDirPath = "/".join(map(str,splitedPath))

            g = git.cmd.Git(gitDirPath)
            updateLog = "[GitUpdate]" + g.pull()

            coreLog.warning(updateLog)
            openbot.sendMessageGroup(updateLog)

            restartPath = os.path.join(os.getcwd(), "restart.py")
            subprocess.Popen([sys.executable, restartPath])
            os._exit(1)
        elif(sendmessage):
            openbot.sendMessageGroup('Обновлений не обнаружено.')
            print('[%s][Updater] Обновлений не обнаружено.'%time.strftime('%Y-%m-%d %H:%M:%S'))


    @staticmethod
    def needUpdate():
        try:
            print('[%s][Updater] Проверка наличия обновлений...'%time.strftime('%Y-%m-%d %H:%M:%S'))

            currentVersion = Util.getCurrentVersion()
            versionAtServer = Util.getVersionAtServer()

            print('[%s][Updater] Текущая версия: %s \n[%s][Updater] Версия на сервере: %s'%(time.strftime('%Y-%m-%d %H:%M:%S'), currentVersion, time.strftime('%Y-%m-%d %H:%M:%S'), versionAtServer))
            
            if(currentVersion < versionAtServer):
                return True

            return False
        except Exception as inst:
            print('[%s][Updater][Exception] %s'%(time.strftime('%Y-%m-%d %H:%M:%S', inst)))
            return False

    @staticmethod
    def getCurrentVersion(): 
        fo = open(os.path.join(os.getcwd(), "version"), "r")
        currentVersion = int(fo.read())
        fo.close()

        return currentVersion
    
    @staticmethod
    def getVersionAtServer():
        updateUrl = "https://raw.githubusercontent.com/partizanes/OkBot/master/OpenContactBot/version"

        with urllib.request.urlopen(updateUrl) as f:
              versionAtServer = int(f.read(10).decode('utf-8'))
              return versionAtServer

    @staticmethod
    def getUpime():
        return  str(datetime.now() - startTime).split('.')[0]