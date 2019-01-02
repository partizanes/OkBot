# -*- coding: utf-8 -*-
# by Part!zanes 2019

from enum import Enum

class Ticket(object):
    def __init__(self, ticket_id, status, client_id, subject, message, client_last_activity, dept_id, ticket_created, sent_date, timezone, email, attachment=None):
        self.ticket_id = ticket_id
        self.status = status
        self.client_id = client_id
        self.subject = subject
        self.message = message
        self.client_last_activity = client_last_activity
        self.dept_id = dept_id
        self.ticket_created = ticket_created
        self.sent_date = sent_date
        self.timezone = timezone
        self.email = email
        self.attachment = attachment

class TicketStatus(Enum):
    NEW     = 1
    OPEN    = 2
    CLOSED  = 3
    ON_HOLD = 4
    SPAM    = 5

    def __str__(self):
        return '%s' % self._value_

class HdTicketStatus(Enum):
    NEW     = 'N'
    OPEN    = 'O'
    CLOSED  = 'C'
    ON_HOLD = 'H'
    SPAM    = 'S'

    def __str__(self):
        return '%s' % self._value_

def getActiveTicketsList():
    return activeTickets

def getActiveRepTicketsList():
    return activeRepTickets

activeTickets = {}
activeRepTickets = {}
