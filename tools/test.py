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
        for i in range(result['TotalCount']):
            if re.match(result['Items'][i]['Vip'][0:6], '10.91.1'):
                continue
            else:
                iplist.append(result['Items'][i]['Vip'])
                labellist.append(result['Items'][i]['InstanceName'])
        return (iplist,labellist)
    except TencentCloudSDKException as err:
        print(err)

if __name__ == '__main__':
    ip = getiplist(1)
    print (type(ip))