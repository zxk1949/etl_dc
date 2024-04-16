from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdb.v20170320 import cdb_client, models
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
import json
import re
import datetime
import os
import pymysql
import time
import requests



#获取iplist (1.主实例，2.只读实例）
def getiplist(role):
    try:
        cred = credential.Credential("AKID0jCLM8EyCBtRowHprSqxlulJcjZ9FTDg", "1lDMDm47uaMq3ye292mHYZXFjQsFMDp6")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdb_client.CdbClient(cred, "ap-beijing", clientProfile)
        req = models.DescribeDBInstancesRequest()
        params1 = '{"InstanceTypes":[1],"Status":[1],"Limit":200}'
        params2 = '{"InstanceTypes":[3],"Status":[1],"Limit":200}'
        if role == 1:
            req.from_json_string(params1)
        elif role == 2:
            req.from_json_string(params2)
        else:
            print ("参数错误")
        resp = client.DescribeDBInstances(req).to_json_string()
        result = json.loads(resp)
        iplist = []
        labellist = []
        blacklist = ['10.89.89.206','10.89.89.141']
        for i in range(result['TotalCount']):
            if re.match(result['Items'][i]['Vip'][0:6], '10.91.1'):
                continue
            elif result['Items'][i]['Vip'] in blacklist:
                continue
            else:
                iplist.append(result['Items'][i]['Vip'])
                labellist.append(result['Items'][i]['InstanceName'])
        return (iplist,labellist)
    except TencentCloudSDKException as err:
        print(err)

#连接池类

class Mysql(object):
    __pool = None
    def __init__(self,ip,db=None):
        self._conn = Mysql.__getConn(ip)
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn(instance_ip):
        """
        @summary: 静态方法，从连接池中取出连接
        @return pymysql.connection
        """
        if Mysql.__pool is None:
            __pool = PooledDB(creator=pymysql, mincached=2 , maxcached=30 ,host=instance_ip , port=3306 , user='root' , passwd='Dba@2019huohua!' , charset='utf8mb4',cursorclass=DictCursor,autocommit=1)
            return __pool.connection()
    def getAll(self,sql,param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result


    def getMany(self,sql,num,param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertOne(self,sql ):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """

        self._cursor.execute(sql )
        return self.__getInsertId()

    def insertMany(self,sql,values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql,values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self,sql,param=None):
        if param is None:

                count = self._cursor.execute(sql)


        else:

                count = self._cursor.execute(sql,param)

        return count

    def update(self,sql,param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def delete(self,sql,param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self,option='commit'):
        """
        @summary: 结束事务
        """
        if option=='commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def close(self):
        """
        @summary: 释放连接池资源
        """
        self._cursor.close()
        self._conn.close()

#dingding推送消息

class dingding:
    def __init__(self):
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token=82a32fbfe0e20a938cd34dca02f7fcf0422e65f7378412425d70163b96e3db67'
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
    def send_msg(self, text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": "notice:{0}".format(text)
            },
            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content



#监控项
class exporter:
    def __init__(self):
        self.dba_pool = Mysql('10.89.87.83','dba')
        self.ip_master = list(getiplist(1))
        self.ip_slave = list(getiplist(2))
        #查看并行线程数
        self.sql1 = "SHOW  STATUS LIKE '%THREADS_RUNNING%'"
        #查看是否有超过半个小时的pt-osc残留表
        self.sql2 = "SELECT table_schema,table_name,create_time FROM information_schema.tables WHERE table_name LIKE '\_%_new' OR table_name LIKE '\_%_old' AND TIMESTAMPDIFF(MINUTE,create_time,NOW()) > 120 AND table_schema NOT IN ('sys','information_schema','performance_schema','mysql')"
        #查看是否有超过半个小时的pt-osc残留触发器
        self.sql3 = "SELECT trigger_schema,trigger_name,created FROM information_schema.triggers WHERE trigger_name LIKE 'pt_osc%' AND TIMESTAMPDIFF(MINUTE,created,NOW()) > 120 AND trigger_schema NOT IN ('sys','information_schema','performance_schema','mysql')"
        #查看主从延迟
        self.sql4 = "show slave status"





    def master_main(self):
        ding = dingding()
        for ip in self.ip_master[0]:
            conn = Mysql(ip)
            result1 = conn.getAll(self.sql1)
            result2 = conn.getAll(self.sql2)
            result3 = conn.getAll(self.sql3)


            if int(result1[0]['Value']) > 20:
                text1 = '{0} 并行线程数为 {1}'.format(self.ip_master[1][self.ip_master[0].index(ip)],result1[0]['Value'])
                ding.send_msg(text1)
            if result2:
                for i in range(len(result2)):
                    text2 = 'label:{0},table_schema:{1},table_name:{2}存在超过120分钟'.format(self.ip_master[1][self.ip_master[0].index(ip)],result2[i]['table_schema'],result2[i]['table_name'])
                    ding.send_msg(text2)
            if result3:
                for i in range(len(result3)):
                    text3 = 'label:{0},trigger_schema:{1},trigger_name:{2}存在超过120分钟'.format(self.ip_master[1][self.ip_master[0].index(ip)],result3[i]['trigger_schema'],result3[i]['trigger_name'])
                    ding.send_msg(text3)
            conn.close()

    def slave_main(self):
        ding = dingding()
        for ip in self.ip_slave[0]:
            conn = Mysql(ip)
            result4 = conn.getAll(self.sql4)
            if int(result4[0]['Seconds_Behind_Master']) > 20:
                text4 = 'label:{0} 主从延迟大于20s,目前延迟为:{1}'.format(self.ip_slave[1][self.ip_slave[0].index(ip)],int(result4[0]['Seconds_Behind_Master']))
                ding.send_msg(text4)
            conn.close()



if __name__ == '__main__':
    while 1 :
        ex = exporter()
        ex.master_main()
        ex.slave_main()
        time.sleep(30)




