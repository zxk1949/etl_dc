
"""
usage: python initial_tecentmysql.py 10.89.87.168
then choose group id
"""


import sys
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdb.v20170320 import cdb_client, models
import json
import pymysql
import re
import time

class initial:
    def __init__(self):
        self.ip = sys.argv[1]
        self.cred = credential.Credential("AKID0jCLM8EyCBtRowHprSqxlulJcjZ9FTDg", "1lDMDm47uaMq3ye292mHYZXFjQsFMDp6")
        self.httpProfile = HttpProfile()
        self.httpProfile.endpoint = "cdb.tencentcloudapi.com"
        self.clientProfile = ClientProfile()
        self.clientProfile.httpProfile = self.httpProfile
        self.client = cdb_client.CdbClient(self.cred, "ap-beijing", self.clientProfile)


    def getinstacne(self):
        try:
            req = models.DescribeDBInstancesRequest()
            params = {
                "InstanceTypes": [1],
                "Vips": [self.ip]
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.DescribeDBInstances(req).to_json_string()
            result = json.loads(resp)
            return (result["Items"][0])

        except TencentCloudSDKException as e:
            print (e)

    def backup_config(self,instance_id):
        try:
            req = models.ModifyBackupConfigRequest()
            params = {
                "InstanceId": instance_id,
                "ExpireDays": 90,
                "BinlogExpireDays": 90
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.ModifyBackupConfig(req)


        except TencentCloudSDKException as e:
            print (e)


    def parameter_config(self,instance_id):
        try:
            req = models.ModifyInstanceParamRequest()
            params = {
                "InstanceIds": [instance_id],
                "ParamList": [
                    {
                        "Name": "binlog_row_image",
                        "CurrentValue": "FULL"
                    },
                    {
                        "Name": "sql_mode",
                        "CurrentValue": "STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION"
                    }
                ]
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.ModifyInstanceParam(req)
        except TencentCloudSDKException as e:
            print (e)

    def create_user(self):
        conn = pymysql.connect(host=sys.argv[1], port=3306, user='root', password='Dba@2019huohua!', db='mysql',
                               charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        sql1="GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'can_r'@'%' identified by 'MmEzZmQ1Nzc2YmVk';"
        sql2="GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, PROCESS, INDEX, ALTER, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT, TRIGGER ON *.* TO 'dbs_user'@'%' identified by 'Uh1U5GOJpeV4IvX9';"
        sql3='flush privileges;'
        cur = conn.cursor()
        cur.execute(sql1)
        cur.execute(sql2)
        cur.execute(sql3)
        cur.close()
        conn.close()

    def dbs_add(self,label,role,ip):
        dbs_conn = pymysql.connect(host='10.89.87.83', port=3306, user='root', password='Dba@2019huohua!', db='archery',charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,autocommit = 1)
        dbs_cur = dbs_conn.cursor()
        sql1 = "INSERT INTO sql_instance (instance_name, type, db_type, host, port, user, password, db_name, charset, service_name, sid,  create_time, update_time) VALUES ('{0}', '{1}', 'mysql', '{2}', 3306, '7tPK9imUBWlvrnFcxJw74g==', 'W-0cWxo9Woyx7PoOi-9uxwZyUlFycZYH-SvJZ76F6y4=', '', '', NULL, NULL, now(), now());".format(label,role,ip)
        sql2 = "select max(id) from sql_instance where host = '{0}';".format(sys.argv[1])
        dbs_cur.execute(sql1)
        dbs_cur.execute(sql2)
        sql_instance_id = dbs_cur.fetchall()
        if role == 'master':
            dbs_cur.execute("INSERT INTO sql_instance_instance_tag (instance_id, instancetag_id) VALUES  ({0}, 1);".format(sql_instance_id[0]['max(id)']))
            sql4 ="select group_id,group_name from resource_group;"
            dbs_cur.execute(sql4)
            result = dbs_cur.fetchall()
            for i in result:
                print (i)
            group_id = input('实例加入组:')
            dbs_cur.execute('INSERT INTO sql_instance_resource_group (instance_id, resourcegroup_id) VALUES ({0}, {1});'.format(sql_instance_id[0]['max(id)'],group_id))
        elif role == 'slave':
            sql5 = 'select resourcegroup_id from sql_instance_resource_group where instance_id={0};'.format(sql_instance_id[0]['max(id)'])
            dbs_cur.execute(sql5)
            result1 = dbs_cur.fetchall()
            print (result1)
            group_id = result1[0]['resourcegroup_id']
            sql6 = "select id from sql_instance where host = '{0}';".format(ip)
            dbs_cur.execute(sql6)
            result2 = dbs_cur.fetchall()
            print (result2)
            instance_id = result2[0]['id']
            dbs_cur.execute(
                'INSERT INTO sql_instance_resource_group (instance_id, resourcegroup_id) VALUES ({0}, {1});'.format(
                    instance_id, group_id))
            dbs_cur.execute("INSERT INTO sql_instance_instance_tag (instance_id, instancetag_id) VALUES  ({0}, 2);".format(instance_id))


        else:
            print("input role;master or slave")


        dbs_cur.close()
        dbs_conn.close()


    def lepus_add(self,label,ip):
        lepus_conn = pymysql.connect(host='10.89.87.83', port=3306, user='root', password='Dba@2019huohua!', db='db_monitor',charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,autocommit = 1)
        lepus_cur = lepus_conn.cursor()
        sql1 = "INSERT INTO db_servers_mysql (host,port,username,password,tags) VALUES ('{0}', 3306, 'root', 'Dba@2019huohua!','{1}');".format(ip,label)
        lepus_cur.execute(sql1)
        lepus_cur.close()
        lepus_conn.close()




if __name__ == '__main__':
    ini = initial()
    result = ini.getinstacne()
    instanceid= result["InstanceId"]
    instancename=result['InstanceName']
    ini.backup_config(instanceid)
    ini.parameter_config(instanceid)
    ini.create_user()
    ini.dbs_add(instancename,'master',sys.argv[1])
    for i in result['RoGroups']:
        ini.dbs_add(i['RoInstances'][0]['InstanceName'],'slave',i['Vip'])
    ini.lepus_add(instancename,sys.argv[1])
    for i in result['RoGroups']:
        ini.lepus_add(i['RoInstances'][0]['InstanceName'],i['Vip'])
    


