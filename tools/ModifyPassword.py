# encoding=utf-8
# 李晓蒙
# 2018-03-15
#每日自动检查数据帐户密码是否过期，过期日为90天。
import os
import sys
import pymysql
sys.path.append('../')
from etc import db_link
from etc import logs
from etc import SendMail
from etc import config

class ModifyPassword:
    def __init__(self):
        self.logs=logs.Log()
        self.dbLink=db_link.DbLink(config.db_host4,config.db_port4,config.db_user4,config.db_password4,config.db_name4,30,1)
        self.dbConn=self.dbLink.get_dblink()

    def checkPassword(self):
        self.sql="SELECT * FROM `pwd_modify_mysql_server` "
        self.rows=self.dbLink.execute_sql(self.dbConn,self.sql)
        for i in self.rows:
            self.userLink=db_link.DbLink(i['db_host'],i['db_port'],i['db_username'],i['db_password'],i['db_name'],30,1)
            self.userConn=self.userLink.get_dblink()
            self.sql='''  SELECT  CONCAT("'",USER,"'",'@',"'",HOST,"'") db_user FROM   `user_view`'''
            self.userRows=self.userLink.execute_sql(self.userConn,self.sql)

            for u in self.userRows:
                self.sql='''INSERT ignore  INTO dba.`pwd_modify_mysql_users` (db_host_id,db_user) VALUES({0},"{1}") '''.format(i['id'],u['db_user'])
                self.dbLink.execute_sql(self.dbConn,self.sql)

            self.sql='SELECT b.db_host,db_user,DATE_ADD(last_modify_time, INTERVAL 90 DAY) exp_time,TIMESTAMPDIFF(DAY,last_modify_time,NOW()) diffday FROM dba.`pwd_modify_mysql_users` a ' \
                     'INNER JOIN dba.`pwd_modify_mysql_server` b ' \
                     'ON a.db_host_id=b.id WHERE TIMESTAMPDIFF(DAY,last_modify_time,NOW())>85'

            self.userList=self.dbLink.execute_sql(self.dbConn,self.sql)

            for user in self.userList:

                if user['diffday']>90:
                    self.sql='GRANT PROCESS ON *.* TO {0} IDENTIFIED BY  "P8WPkW43l50Nkeo848HKxObbcu743AL1" ;flush privileges ;'.format(user['db_user'])
                    self.userLink.execute_sql(self.userConn,self.sql)
                    self.send=SendMail.SendMail()
                    self.receiver=i['receive_user'].strip(',').split(',')
                    self.send.Send(self.receiver,"{0} 密码到期帐户已停用".format(user['db_user']),"  实例：%s \n  用户名：%s \n  密码到期时间：%s  \n  此帐户已被禁用！！！"%(user['db_host'],user['db_user'],user['exp_time']),'')
                else:
                    self.send=SendMail.SendMail()
                    self.receiver=i['receive_user'].strip(',').split(',')
                    self.send.Send(self.receiver,'发现数据库密码即将到期',  "  实例：%s \n  用户名：%s \n  到期时间：%s  \n  到期后数据库密码将被重置"%(user['db_host'],user['db_user'],user['exp_time']),'')

            self.userConn.close()
            self.dbConn.close()



if __name__ == '__main__':
    modifyPassword=ModifyPassword()
    modifyPassword.checkPassword()

