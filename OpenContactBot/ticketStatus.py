# -*- coding: utf-8 -*-
# by Part!zanes 2017

from enum import Enum

class TicketStatus(Enum):
    NEW     = 1
    OPEN    = 2
    CLOSED  = 3
    ON_HOLD = 4
    SPAM    = 5

    #def __str__(self):
    #    return '%s' % self._value_