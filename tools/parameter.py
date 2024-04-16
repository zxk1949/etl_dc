from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdb.v20170320 import cdb_client, models
import json
import re
from exporter import config
import pymysql


class tencent:
    def __init__(self):
        self.cred = credential.Credential("AKID0jCLM8EyCBtRowHprSqxlulJcjZ9FTDg", "1lDMDm47uaMq3ye292mHYZXFjQsFMDp6")
        self.blacklist = config.blacklist
    def getiplist(self,role):
        try:
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cdb.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cdb_client.CdbClient(self.cred, "ap-beijing", clientProfile)
            req = models.DescribeDBInstancesRequest()
            params1 = '{"InstanceTypes":[1],"Status":[1],"Limit":1000}'
            params2 = '{"InstanceTypes":[3],"Status":[1],"Limit":1000}'
            params3 = '{"InstanceTypes":[1,3],"Status":[1],"Limit":1000}'
            iplist = []
            labellist = []
            if role in [1,2,3]:
                if role == 1:
                    req.from_json_string(params1)
                elif role == 2:
                    req.from_json_string(params2)
                elif role == 3:
                    req.from_json_string(params3)
                resp = client.DescribeDBInstances(req).to_json_string()
                result = json.loads(resp)
                for i in range(result['TotalCount']):
                    if re.match(result['Items'][i]['Vip'][0:6], '10.91.1') or re.match(result['Items'][i]['Vip'][0:8], '10.89.254') :
                        continue
                    elif result['Items'][i]['Vip'] in self.blacklist:
                        continue
                    else:
                        iplist.append(result['Items'][i]['Vip'])
                        labellist.append(result['Items'][i]['InstanceName'])
                if role == 2:
                    iplist.extend(config.datacenter_ip)
                    labellist.extend(config.datacenter_label)
                    iplist.append(config.sim_ip[0])
                    labellist.append(config.sim_label[0])
            elif role == 4:
                iplist.extend(config.qa_dev_list)
                labellist.extend(config.qa_dev_label)
                iplist.append(config.sim_ip[1])
                labellist.append(config.sim_label[1])
            return (iplist,labellist)
        except TencentCloudSDKException as err:
            print(err)



if __name__ == '__main__':
    tengxun = tencent()
    sql = "SHOW VARIABLES LIKE 'tx_isolation';"
    resultlist = list(tengxun.getiplist(1))
    for ip in resultlist[0]:
        conn = pymysql.connect(host=ip, user='root',password='Dba@2019huohua!',database='mysql',charset='utf8mb4')
        cursor = conn.cursor()
        cursor.execute(sql)
        result = list(cursor.fetchall())
        print (resultlist[1][resultlist[0].index(ip)],result)



