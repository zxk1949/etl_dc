# encoding=utf-8
import os,sys
import datetime
import time
import pymysql as db
from pymysql.cursors import DictCursor
class KillProcess():
    def __init__(self):
        pass

    def killProc(self,host,port,username,password):
        print (host,port,username,password)
        self.dbconn = db.connect(host=host, port=int(port), user=username, passwd=password, db='information_schema', charset='utf8', autocommit=1,cursorclass=DictCursor)
        self.cor=self.dbconn.cursor()
        self.cor.execute(" SELECT * FROM `information_schema`.`PROCESSLIST` WHERE USER='{0}'".format(username))
        self.result = self.cor.fetchall()
        self.killconn = db.connect(host=host, port=int(port), user=username, passwd=password, db='information_schema', charset='utf8', autocommit=1,cursorclass=DictCursor)
        self.killcor=self.killconn.cursor()

        for row in self.result:
            print (row)
            self.killsql='kill {0}'.format(row["ID"])
            print (self.killsql)
            self.killcor.execute(self.killsql)
if __name__ == '__main__':

    killPorcess=KillProcess()
    killPorcess.killProc(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
