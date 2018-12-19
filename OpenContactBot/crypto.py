# -*- coding: utf-8 -*-
# by Part!zanes 2017

import rsa
import base64
from config import Config as cfg

class Crypto(object):
    @staticmethod
    def getKey():
        n,e,d,p,q =  map(int, cfg.getPrivatekey())
        return rsa.PrivateKey(n,e,d,p,q)

    def encode(value):
        n,e,d,p,q =  map(int, cfg.getPrivatekey())
        key = rsa.PrivateKey(n,e,d,p,q)
        public_key = rsa.PublicKey(n,e)

        rsa_enc =  rsa.encrypt(value.encode('UTF-8'), public_key)
        print(rsa_enc)
        base64value = base64.b64encode(rsa_enc)
        print(base64value)
        rsa_dec = rsa.decrypt(base64.b64decode(base64value), key).decode('UTF-8')
        print(rsa_dec)

        return base64value

    def decode(value):
        cfg.initializeConfig()

        n,e,d,p,q =  map(int, cfg.getPrivatekey())
        key = rsa.PrivateKey(n,e,d,p,q)

        public_key = rsa.PublicKey(n,e)
        rsa_dec = rsa.decrypt(base64.b64decode(value), key).decode('UTF-8')
        print(rsa_dec)

        return(rsa_dec)


    @staticmethod
    def getDomainUsername():
        return rsa.decrypt(base64.b64decode(cfg.getDomainUsername()), Crypto.getKey()).decode('UTF-8')

    @staticmethod
    def getDomainPassword():
        return rsa.decrypt(base64.b64decode(cfg.getDomainPassword()), Crypto.getKey()).decode('UTF-8')