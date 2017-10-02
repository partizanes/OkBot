# -*- coding: utf-8 -*-
# by Part!zanes 2017

class Ticket(object):
    def __init__(self, ticket_id, status, client_id, subject, message, client_last_activity, dept_id, ticket_created, sent_date, timezone, email):
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

def getActiveTicketsList():
    return activeTickets

def getActiveRepTicketsList():
    return activeRepTickets

activeTickets = {}
activeRepTickets = {}
