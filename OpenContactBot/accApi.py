# -*- coding: utf-8 -*-
# by Part!zanes 2019

import time, hashlib, requests

from log import Log
from config import Config

log = Log('accApi')
API_HOST = Config.getAccApiHost()

def getDataFromApi(url_part):
    """Get json data from api by email. If more than timeout return from cache"""
    try:
        data = {'token': createToken()}

        r = requests.get(API_HOST +  url_part, params=data)

        return r.json()['data']
    except Exception as exc:
        log.critical("[getDataFromApi] {0}".format(exc.args))
    
    return None

def createToken():
    return hashlib.sha256((Config.getAccApiToken() + str(int(time.time() // 60))).encode()).hexdigest()