# -*- coding: utf-8 -*-
# by Part!zanes 2017

import MySQLdb
from log import Log
from datetime import datetime
from config import Config as cfg
from crypto import Crypto as crt


class Datebase(object):
    cfg.initializeConfig()
    dbLog = Log('Datebase')

    def __init__(self):
        self.conn = MySQLdb.connect(host=cfg.getNameHost(),user=crt.getMysqlUser(),
                  passwd=crt.getMysqlPass(),db=cfg.getDbName(),charset = cfg.getDbCharset())
        self.cur = self.conn.cursor()
    
    def query(self,sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def rows(self):
        return self.cur.rowcount

    def __enter__(self):
        return Datebase()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
    
    def getNewTicketsRows(self):
        sql = """
            SELECT hdp_tickets.ticket_id,STATUS,hdp_tickets.client_id,hdp_tickets.subject,message,
            client_last_activity,dept_id,ticket_created,sent_date,timezone,hdp_clients.email FROM hdp_tickets 
            LEFT OUTER JOIN hdp_ticket_replies ON hdp_tickets.ticket_id = hdp_ticket_replies.ticket_id
            LEFT JOIN hdp_clients ON hdp_tickets.client_id = hdp_clients.client_id
            WHERE hdp_tickets.status = 'N' AND hdp_tickets.dept_id = 2 AND assigned_to = 0 
            AND hdp_ticket_replies.ticket_id IS NULL
            """

        #self.dbLog.warning(sql + '\n')

        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def getRepliesTicketsIdList(self):
        #Ticket with replies and status Open and Hold
        sql = """
            SELECT ticket_id FROM hdp_tickets LEFT OUTER JOIN hdp_ticket_priorities_ru ON hdp_tickets.priority_id=hdp_ticket_priorities_ru.priority_id ,
            hdp_ticket_status_ru, hdp_departments, hdp_staff_departments, hdp_clients WHERE hdp_tickets.status=hdp_ticket_status_ru.status_key AND 
            hdp_tickets.dept_id=hdp_departments.dept_id AND hdp_tickets.dept_id=hdp_staff_departments.dept_id AND hdp_tickets.client_id=hdp_clients.client_id
            AND hdp_staff_departments.staff_id='103' AND  hdp_tickets.status IN ('O','H') AND hdp_tickets.updater = 'CLIENT'
            """

        self.cur.execute(sql)
        
        list = []

        for row in self.cur.fetchall():
            list.append(row[0])

        #ticket without ticket marker (Status new ticket ,but have replies)
        sql = """
            SELECT hdp_ticket_replies.ticket_id, change_status, hdp_ticket_replies.reporter_id, hdp_ticket_replies.subject, hdp_ticket_replies.reply, client_last_activity, hdp_tickets.dept_id, ticket_created, sent_date, timezone, hdp_clients.email FROM hdp_tickets 
	        LEFT JOIN `hdp_ticket_replies` ON hdp_ticket_replies.ticket_id = hdp_tickets.ticket_id
	        LEFT OUTER JOIN hdp_ticket_priorities_ru ON hdp_tickets.priority_id=hdp_ticket_priorities_ru.priority_id ,
            hdp_ticket_status_ru, hdp_departments, hdp_staff_departments, hdp_clients WHERE hdp_tickets.status=hdp_ticket_status_ru.status_key AND 
            hdp_tickets.dept_id=hdp_departments.dept_id AND hdp_tickets.dept_id=hdp_staff_departments.dept_id AND hdp_tickets.client_id=hdp_clients.client_id
            AND hdp_staff_departments.staff_id='103' AND  hdp_tickets.status IN ('N') AND hdp_tickets.updater = 'CLIENT' AND hdp_ticket_replies.ticket_id IS NOT NULL ORDER BY replied_on LIMIT 1
            """

        self.cur.execute(sql)

        for row in self.cur.fetchall():
            list.append(row[0])

        return list

    def getLastRepliesByTicketId(self, ticket_id):
        sql = """
        SELECT hdp_ticket_replies.ticket_id, change_status, hdp_ticket_replies.reporter_id, hdp_ticket_replies.subject, reply, client_last_activity, dept_id, ticket_created, sent_date, timezone, hdp_clients.email FROM hdp_ticket_replies
        LEFT JOIN `hdp_tickets` ON hdp_tickets.ticket_id = hdp_ticket_replies.ticket_id
        LEFT JOIN `hdp_clients` ON hdp_clients.client_id = hdp_ticket_replies.reporter_id 
        WHERE hdp_ticket_replies.ticket_id = '%s' AND hdp_ticket_replies.reporter_id <> 103  ORDER BY replied_on DESC LIMIT 1
        """ %(ticket_id)

        self.cur.execute(sql)
        return self.cur.fetchall()

    def setTicketClose(self, ticket_id):
        sql = "UPDATE hdp_tickets SET status = 'C' WHERE `ticket_id` = '%s'"  % ticket_id
        
        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

        self.addPrivateReply(ticket_id,'[OpenContactBot] Заявка закрыта.')
    
    def setTicketSpam(self, ticket_id):
        sql = "UPDATE hdp_tickets SET status = 'S' WHERE `ticket_id` = '%s'"  % ticket_id

        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

        self.addPrivateReply(ticket_id,'[OpenContactBot] Перемещено в спам.')
    
    def setTickethold(self, ticket_id):
         sql = "UPDATE hdp_tickets SET status = 'H', updater_id = 103, updater='STAFF' WHERE `ticket_id` = '%s'"  % ticket_id

         self.dbLog.warning(sql + '\n')
         self.cur.execute(sql)
         self.cur.fetchone()

         self.addPrivateReply(ticket_id,'[OpenContactBot] Перемещено в задержанные.')

    def moveTicketTo(self, dept_id, ticket_id):
        sql = "UPDATE hdp_tickets SET dept_id = %i , server_id = %i WHERE ticket_id = '%s'" %(dept_id, dept_id, ticket_id)

        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

    def addPrivateReply(self, ticket_id, message):
        sql = """
            insert into hdp_ticket_replies (reporter_id,ticket_id,replied_on,reply,reporter,subject,
            change_status,private,readflag,draft,internal_message,reply_minutes,responded_from,resolution_item)
            values ('103', '%s', '%s', '%s', 'STAFF', '', '', '1', '', '', '', '0', '2', '0' )
        """ %(ticket_id, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), message)

        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

    def getSpamEmail(self):
        sql = "SELECT sp_addresses FROM hdp_spam_message"
        self.cur.execute(sql)
        return self.cur.fetchall()[0][0]

    def setSpamEmail(self, email):
        current = self.getSpamEmail()
        current += '\r\n%s' %(email)

        sql = "UPDATE hdp_spam_message SET sp_addresses = '%s' WHERE spm_id = 5" %(current)

        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

    def getEmailByTicketId(self, ticket_id):
         sql = """SELECT email FROM `hdp_tickets` 
         LEFT JOIN hdp_clients ON hdp_tickets.client_id = hdp_clients.client_id 
         WHERE `ticket_id` = '%s'
         """ %(ticket_id)
         
         self.cur.execute(sql)
         return self.cur.fetchall()[0][0]