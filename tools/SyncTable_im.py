# encoding=utf-8
import os, sys
import time
import re
sys.path.append('../')
sys.path.append('./')
import datetime
import DateTool
import subprocess
from etc import logs
from etc import MysqlPool
from etc import SendMail


class SyncTable():
    def __init__(self):
        self.dateTool=DateTool.DateTool()
        self.sql = ''
        self.log = logs.Log()
        self.receiver = ['duanzexun@huohua.cn']
        #self.dba_db = MysqlPool.Mysql('huohuadev')


    def sync(self,dbsource,sourceTableName,columnName,descTableName,days,interval=1,filter=''):
        if filter !='':
            filter=" and {0} ".format(filter)
        self.sourcedb = MysqlPool.Mysql(dbsource)
        self.descdb = MysqlPool.Mysql(dbsource)
        self.today = datetime.datetime.now()- datetime.timedelta(days=days)
        self.today_date=self.today.strftime("%Y-%m-%d")
        self.yesterday = self.today - datetime.timedelta(days=interval)
        self.yesterday_date = self.yesterday.strftime("%Y-%m-%d")
        startDT=self.yesterday_date
        endDT=self.today_date
        print (startDT,endDT)
        while startDT<endDT:
            # print (startDT,endDT)
            self.log.writeLog.info('开始归档： {0}.{1} {2} 的数据'.format(dbsource, sourceTableName, startDT))

            nextEndDt=self.dateTool.addDatetime(startDT,1)
            self.sql="select min(id) minid,max(id) maxid from {0} where {1} >='{2}' and {1} <'{3}' {4}".format(sourceTableName,columnName,startDT,nextEndDt,filter)
            # print (self.sql)

            self.result=self.sourcedb.getAll(self.sql)

            self.result=self.result[0]
            # print (self.result['minid'])

            if self.result['minid']:

                while self.result["minid"]<self.result["maxid"]+1:
                    self.nextId=self.result["minid"]+2000
                    if self.nextId>self.result["maxid"]:
                        self.nextId=self.result["maxid"]+1
                    self.sql = "delete from {0} where id >={1} and id <{2} and {3} >='{4}' and {3} <'{5}' {6}".format(descTableName, self.result["minid"],
                                                                                    self.nextId ,columnName,startDT,nextEndDt,filter)
                    # print (self.sql)
                    try:
                        self.descdb.delete(self.sql)
                    except Exception as e:
                        self.log.writeLog.error(
                            "数据库归档异常  表名：{0}，sql: {1}  error:{2}".format(descTableName, self.sql, str(e)))
                        self.sendMail = SendMail.SendMail()
                        self.sendMail.Send(self.receiver, '数据库归档异常',
                                           '数据库归档异常  表名：{0}，sql: {1}  error:{2}'.format(descTableName, self.sql,
                                                                                        str(e)),
                                           '')
                        exit(0)

                    self.sql="insert into {3} select * from {0} where id >={1} and id <{2} and {4} >='{5}' and {4} <'{6}' {7}".format(sourceTableName,self.result["minid"],self.nextId,descTableName,columnName,startDT,nextEndDt,filter)
                    # print (self.sql)
                    try:
                        self.descdb.insertOne(self.sql)
                    except Exception as e:
                        self.log.writeLog.error("数据库归档异常  表名：{0}，sql: {1}  error:{2}".format(sourceTableName,self.sql, str(e)))
                        self.sendMail = SendMail.SendMail()
                        self.sendMail.Send(self.receiver, '数据库归档异常', '数据库归档异常  表名：{0}，sql: {1}  error:{2}'.format(sourceTableName,self.sql, str(e))  , '')
                        exit(0)

                    try:
                        self.sql ="delete from {0} where id >={1} and id <{2} and {3} >='{4}' and {3} <'{5}' {6}".format(sourceTableName, self.result["minid"],
                                                                                    self.nextId ,columnName,startDT,nextEndDt,filter)
                        # print (self.sql)
                        self.sourcedb.delete(self.sql)
                    except Exception as e:
                        self.log.writeLog.error(
                            "数据库归档异常  表名：{0}，sql: {1}  error:{2}".format(sourceTableName, self.sql, str(e)))
                        self.sendMail = SendMail.SendMail()
                        self.sendMail.Send(self.receiver, '数据库归档异常',
                                           '数据库归档异常  表名：{0}，sql: {1}  error:{2}'.format(sourceTableName, self.sql,
                                                                                        str(e)),
                                           '')
                        exit(0)
                    time.sleep(2)
                    self.result["minid"]=self.result["minid"]+2000
            self.log.writeLog.info('归档完成： {0}.{1} {2} 的数据'.format(dbsource, sourceTableName, startDT))
            startDT=self.dateTool.addDatetime(startDT,1)


if __name__ == '__main__':
    syncTable=SyncTable()
    #syncTable.sync('peppa','mall_remind_message','send_time','mall_remind_message_history',31,1)
    #syncTable.sync('peppa','operate_log', 'created_time', 'operate_log_history', 90,1)
    #syncTable.sync('xxl-job', 'XXL_JOB_QRTZ_TRIGGER_LOG', 'trigger_time', 'XXL_JOB_QRTZ_TRIGGER_LOG_HISTORY', 31, 1)
    # syncTable.sync('crm', 'customer_order', 'created_time', 'customer_order_history', 3, 1,'pay_price = 0')
    #syncTable.sync('push_service', 'sms', 'create_time', 'sms_history', 50, 1, '')
    #syncTable.sync('immanager', 'im_loginout_history', 'date_when', 'im_loginout_history_20201211_later', 30, 1, '')
    #syncTable.sync('sa_xxljob', 'xxl_job_log', 'trigger_time', 'xxl_job_log_history', 30, 1, '')
    syncTable.sync('immanager', 'im_loginout_history', 'login_when', 'im_loginout_history_20201211_later', 15, 500, '')
    #syncTable.sync('immanager', '', 'created_when', 'im_pmsg_pendingprocess_20210113_later', 30,500, '')
    ##syncTable.sync('immanager', 'im_pmsg_pendingprocess', 'created_when', 'im_pmsg_pendingprocess_20210113_later', 30, 1, '')
    #syncTable.sync('immanager', 'im_pmsghistory', 'sent_when', 'im_pmsghistory_history_new', 30, 500, '')
    #syncTable.sync('opengalaxy', 'msc_clienttrenddata', 'report_time', 'msc_clienttrenddata_history', 30, 1, '')
    #syncTable.sync('impush', 'error_info', 'create_time', 'error_history', 31, 1,'')
    #syncTable.sync('impush', 'register_record', 'created_time', 'register_record_history', 200, 1,'')
    #syncTable.sync('ticket', 'ticket', 'created_time', 'ticket_history', 365, 1,'')

    # syncTable.sync('master_sim_payment', 'pay_deposit_order', 'pay_time', 'pay_deposit_order_history', 202, 1000,' account_type = 300  ')
    # syncTable.sync('peppa', 'student_reward_detail', 'award_time', 'student_reward_detail_history', 100, 1000,'((sumd=1 AND award_reason=12 ) OR award_reason IN(1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83))')
