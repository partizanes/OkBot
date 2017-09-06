# -*- coding: utf-8 -*-
# by Part!zanes 2017

from enum import Enum

class hdDepartaments(Enum):
    HOSTING     = 2
    EASYPAY     = 3
    TEST        = 4
    DOMAIN      = 5
    RABOTA      = 6
    WINSHOP     = 10

    def __str__(self):
        return '%s' % self._value_
       
