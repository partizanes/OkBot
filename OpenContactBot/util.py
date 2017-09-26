# -*- coding: utf-8 -*-
# by Part!zanes 2017
import os
import sys
import urllib.request

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
    def needUpdate():
        try:
            updateUrl = "https://raw.githubusercontent.com/partizanes/OkBot/master/OpenContactBot/version"
            patchToVersion = os.path.join(os.getcwd(), "version")

            fo = open(patchToVersion, "r")
            currentVersion = int(fo.read())
            fo.close()

            with urllib.request.urlopen(updateUrl) as f:
              versionAtServer = int(f.read(10).decode('utf-8'))

            if(currentVersion != versionAtServer):
                return True

            return False
        except Exception as inst:
            return False
