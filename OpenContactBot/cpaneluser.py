# -*- coding: utf-8 -*-
# by Part!zanes 2017

class cpanelUser(object):
    def __init__(self, username, domain, server, email, package):
        self.username = username
        self.domain   = domain
        self.server   = server
        self.email    = email
        self.package     = package

        