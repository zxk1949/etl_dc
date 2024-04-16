import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.redis.v20180412 import redis_client, models
import datetime
import subprocess
import os
today = today = datetime.datetime.today()
backup_begin_time = datetime.datetime(today.year, today.month, today.day, 4, 30, 0)
backup_end_time = datetime.datetime(today.year, today.month, today.day, 5, 30, 0)
def get_backup_id(instance_id):
    try:
        cred = credential.Credential("AKID0jCLM8EyCBtRowHprSqxlulJcjZ9FTDg", "1lDMDm47uaMq3ye292mHYZXFjQsFMDp6")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "redis.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = redis_client.RedisClient(cred, "ap-beijing", clientProfile)

        req = models.DescribeInstanceBackupsRequest()
        params = {
            "Status": [ 2 ],
            "InstanceId": instance_id,
            "BeginTime": backup_begin_time.strftime("%Y-%m-%d %H:%M:%S"),
            "EndTime": backup_end_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        req.from_json_string(json.dumps(params))

        resp = eval(client.DescribeInstanceBackups(req).to_json_string())
        return resp["BackupSet"][0]["BackupId"]

    except TencentCloudSDKException as err:
        print(err)

def get_backup_url(instance_id,backupid):
    try:
        cred = credential.Credential("AKID0jCLM8EyCBtRowHprSqxlulJcjZ9FTDg", "1lDMDm47uaMq3ye292mHYZXFjQsFMDp6")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "redis.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = redis_client.RedisClient(cred, "ap-beijing", clientProfile)

        req = models.DescribeBackupUrlRequest()
        params = {
            "BackupId": backupid,
            "InstanceId": instance_id
        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeBackupUrl(req).to_json_string()
        url = eval(resp)["DownloadUrl"][0]
        return  (url)

    except TencentCloudSDKException as err:
        print(err)


if __name__ == '__main__':
    backupid=get_backup_id()
    url = get_backup_url(backupid)
    name = 'im.rdb'
    cmd_backup = "wget -O %s '%s'" % (name,url)
    cmd_restore = "/root/redis-shake-1.6.24/redis-shake.linux -type=restore -conf=/root/redis-shake-1.6.24/im_restore.conf"
    cmd_delete = "rm -rf /data0/dba/im.rdb"
    cmd_flush = "cat /root/redis-shake-1.6.24/flushtest.txt | redis-cli  -h r-2zehk7q18eqesx7ees.redis.rds.aliyuncs.com -a AcUVeRb8lN"
    subprocess.call(cmd_delete, shell=True)
    subprocess.call(cmd_backup, shell=True)
    subprocess.call(cmd_flush ,  shell=True)
    subprocess.call(cmd_restore, shell=True)


