# -*- coding: utf-8 -*-
# by Part!zanes 2017

import time
import pickle
from log import Log
from util import Util as u

cacheDir = u.get_script_path() + '/cache'
cacheLog = Log('CacheLog')

def save_obj(obj, name ):

    u.createDir(cacheDir)

    with open('cache/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('cache/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def isOutdated(name):
    filePath = u.patchJoin(cacheDir,name + '.pkl')

    if u.fileExits(filePath):
        fileChangeTime = u.getFileChangeTime(filePath)

        #File older then 5 hours outdated
        if(time.time() - fileChangeTime >  18000):
            cacheLog.info('Cache %s outdated.' %(name))
            return True
    else:
        cacheLog.info('Cache %s doesn`t exits.' %(name))
        return True

    cacheLog.info('Cache %s active.' %(name))
    return False

def getTimeToStartCron(name):
    filePath = u.patchJoin(cacheDir,name + '.pkl')

    if u.fileExits(filePath):
        fileChangeTime = u.getFileChangeTime(filePath)

        timeToStart = (18001 -(time.time() - fileChangeTime))

        if timeToStart > 0:
            return timeToStart

    return 60