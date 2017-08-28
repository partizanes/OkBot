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

    @staticmethod
    def getCpanelPass():
        return rsa.decrypt(base64.b64decode(cfg.getCpanelPass()), Crypto.getKey()).decode('UTF-8')

    @staticmethod
    def getCpanelToken(value):
        return rsa.decrypt(base64.b64decode(cfg.getCpanelToken(value)), Crypto.getKey()).decode('UTF-8')

    @staticmethod
    def getDomainUsername():
        return rsa.decrypt(base64.b64decode(cfg.getDomainUsername()), Crypto.getKey()).decode('UTF-8')

    @staticmethod
    def getDomainPassword():
        return rsa.decrypt(base64.b64decode(cfg.getDomainPassword()), Crypto.getKey()).decode('UTF-8')

    def getConfigCriptedValue(value):
        n,e,d,p,q =  map(int, cfg.getPrivatekey().split(","))
        key = rsa.PrivateKey(n,e,d,p,q)
        public_key = rsa.PublicKey(n,e)

        rsa_enc =  rsa.encrypt(value.encode('UTF-8'), public_key)
        print(rsa_enc)
        base64value = base64.b64encode(rsa_enc)
        print(base64value)
        rsa_dec = rsa.decrypt(base64.b64decode(base64value), key).decode('UTF-8')
        print(rsa_dec)

        return base64value
