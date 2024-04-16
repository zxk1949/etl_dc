# encoding=utf-8

import datetime
import os,sys
import time
import pymysql
sys.path.append('../')
from etc import db_link
from etc import logs
from etc import SendMail
from etc import config

class SyncDb():
    def __init__(self):
        self.bakupFile='/opt/data/backup.sql'

    def backupDB(self):
        self.cmd='/usr/bin/mysqldump -h10.89.89.61 -uroot -pDba@2019huohua! --set-gtid-purged=OFF   --flush-logs --master-data=2 --single-transaction  --default-character-set=utf8 --databases peppa >{0}'.format(self.bakupFile)
        info=os.popen(self.cmd).readlines()

    def restoreDB(self):
        self.cmd='/usr/bin/mysqldump -h172.16.208.79 -uroot -p6jRLTpKD5P peppa <{0}'.format(self.bakupFile)
        info=os.popen(self.cmd).readlines()

if __name__ == '__main__':
    syncDb=SyncDb()
    syncDb.backupDB()

