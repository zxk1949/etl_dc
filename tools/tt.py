# encoding=utf-8
import os, sys
import pymysql
import re

sys.path.append('../')
sys.path.append('./')
from etc import logs
from etc import MysqlPool
import time


class test():
    def __init__(self):
        self.sql = ''
        self.log = logs.Log()
        #self.dba_db = MysqlPool.Mysql('huohuadev')
        self.db_sync_sim_mysql=MysqlPool.Mysql("sync_sim_mysql")
        self.db_master_sim_mysql = MysqlPool.Mysql("master_sim_mysql")
    def t1(self):
        rows=self.db_master_sim_mysql.getAll('SELECT id,NAME FROM agent.`agent` LIMIT 2 ')
        print(rows)
if __name__ == '__main__':
    t=test()
    t.t1()