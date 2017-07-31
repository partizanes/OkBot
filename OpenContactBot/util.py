# -*- coding: utf-8 -*-
# by Part!zanes 2017
import os
import sys

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