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

    def setTicketClose(self,ticket_id):
        sql = "UPDATE hdp_tickets SET status = 'C' WHERE `ticket_id` = '%s'"  % ticket_id
        
        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

        self.addPrivateReply(ticket_id,'[OpenContactBot] Заявка закрыта.')

    def addPrivateReply(self,ticket_id,message):
        sql = """
            insert into hdp_ticket_replies (reporter_id,ticket_id,replied_on,reply,reporter,subject,
            change_status,private,readflag,draft,internal_message,reply_minutes,responded_from,resolution_item)
            values ('103', '%s', '%s', '%s', 'STAFF', '', '', '1', '', '', '', '0', '2', '0' )
        """ %(ticket_id, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), message)

        self.dbLog.warning(sql + '\n')
        self.cur.execute(sql)
        self.cur.fetchone()

        