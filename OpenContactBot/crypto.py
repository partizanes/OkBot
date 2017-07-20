# -*- coding: utf-8 -*-
# by Part!zanes 2017

import rsa
import base64
from config import Config as cfg

class Crypto(object):
    @staticmethod
    def getKey():
        n,e,d,p,q =  map(int, cfg.getPrivatekey().split(","))
        return rsa.PrivateKey(n,e,d,p,q)

    @staticmethod
    def getMysqlUser():
        return rsa.decrypt(base64.b64decode(cfg.getMysqlUser()), Crypto.getKey()).decode('UTF-8')

    @staticmethod
    def getMysqlPass():
        return rsa.decrypt(base64.b64decode(cfg.getMysqlPass()), Crypto.getKey()).decode('UTF-8')