import pymysql
import time
from etc import MysqlPool
import datetime


db = MysqlPool.Mysql('multi_region')
result1 = db.getAll('show databases;')
db_list = []
for i in result1:
    if i['Database'] not in ['information_schema','mysql','performance_schema','sys']:
        db_list.append(i['Database'])
#print (db_list)

for j in db_list:
    table_list=[]
    result2 = db.getAll('select * from information_schema.tables where table_schema="{0}"'.format(j))
    for k in result2:
        time1= datetime.datetime.now()
        result3 = db.getAll('select count(*) from {0}.{1};'.format(j,k['TABLE_NAME']))
        time2 = datetime.datetime.now()
        ms = time2 - time1
        #print (j,k['TABLE_NAME'],ms.microseconds/1000)
        print(ms.microseconds/1000)

