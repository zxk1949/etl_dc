# encoding=utf-8
import os, sys
import time
import re
sys.path.append('../')
sys.path.append('./')
import datetime

import subprocess
from etc import logs
from etc import MysqlPool
from etc import SendMail


class BachInsert():
    def __init__(self):

        self.sql = ''
        self.log = logs.Log()
        self.receiver = ['lixiaomeng@huohua.cn']
        self.crm_db = MysqlPool.Mysql('crm')
    def bachInsert(self):
        num =0
        while num <162735376:
            self.sql=' UPDATE crm.call_data_record SET end_reason = "主通道挂机" WHERE id >={0} and id<{1} and  end_reason = "是";'.format(num,num+1000)
            count=self.crm_db.update(self.sql)
            # print(count)
            if count>500:
                time.sleep(1)
            elif count>200:
                time.sleep(0.2)
            self.sql="UPDATE crm.call_data_record SET end_reason = '非主通道挂机' WHERE  id >={0} and id<{1} and  end_reason = '否';".format(num,num+1000)
            count=self.crm_db.update(self.sql)
            if count>500:
                time.sleep(1)
            elif count>200:
                time.sleep(0.2)
            num=num+1000
            if num%100000==0:
                print("已处理{0}行".format(num))
if __name__ == '__main__':
    bachInsert=BachInsert()
    bachInsert.bachInsert()


