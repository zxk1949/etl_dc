import sys
import os
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
sys.path.append('../')
from etc import MysqlPool
import time
from tools import DingtalkApi
dingsender = DingtalkApi.Sender()


class Check_consistance:
    def __init__(self):
        self.manage_pool=MysqlPool.Mysql("dba")
     #   self.table_list = eval(self.config[0]['tables'])
        self.source_pool = MysqlPool.Mysql("datacenter")
        self.target_pool = MysqlPool.Mysql("dc")

    def main(self):
        etl_list=[]
        etl_list_sql = "select etl_name from etl_config where etl_name like '%dc'"
        time1 = time.strftime("%Y-%m-%d", time.localtime())
        for i in self.manage_pool.getAll(etl_list_sql):
            etl_list.append(i['etl_name'])
        for j in etl_list:
            etl_result_sql = "select * from etl_config where etl_name ='{0}' limit 1".format(j)
            etl_result = self.manage_pool.getAll(etl_result_sql)
            etl_table_list = self.target_pool.getAll("select table_name from information_schema.tables where table_schema='{0}'".format(etl_result[0]["rewrite_db"]))
            try:
                for table_dict in etl_table_list:
                    desc1 = self.source_pool.getAll("desc {0}.{1}".format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))
                    desc2 = self.target_pool.getAll("desc {0}_sync.{1}".format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))
                    if desc1 !=desc2:
                        if len(desc1) != len(desc2):
                            #print('{0}.{1}  字段数量不同'.format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))
                            dingsender.send('{0}.{1}  字段数量不同 \n'.format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))
                        else:
                            for i in range(len(desc2)):
                                #print (desc1[i])
                                if desc1[i] != desc2[i]:
                                    #print ('{0}.{1} {2} 不同'.format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"],desc2[i]))
                                    dingsender.send('{0}.{1} {2} 不同 \n'.format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"],desc2[i]))

                        #print ('{0}.{1} 表结构不同'.format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))
                        dingsender.send('{0}.{1} 表结构不同 \n'.format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))

                    source_max_id = self.source_pool.getAll("select max(id) from {0}.{1} ".format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"]))[0]['max(id)']
                    count_source = self.source_pool.getAll("select count(*) from {0}.{1} where id < {2}".format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"],source_max_id))
                    count_target = self.source_pool.getAll("select count(*) from {0}_sync.{1} where id < {2}".format(eval(etl_result[0]['source_db'])[0],table_dict["table_name"],source_max_id))
                    if count_source[0]['count(*)'] != count_target[0]['count(*)']:
                        #print ('{0} count不同'.format(table_dict["table_name"]))
                        dingsender.send('{0} count不同 \n'.format(table_dict["table_name"]))

            except Exception as e:
                print (e)
                continue











if __name__ == '__main__':
    check = Check_consistance()
    check.main()




