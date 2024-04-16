import redis
import subprocess
import os
from etc import MysqlPool
import time


class redis_monitor:
    def __init__(self):
        self.dba_pool = MysqlPool.Mysql('dba')

    def redis_client(self, ip, pwd):
        cmd = "redis-cli -h {0} -a {1} client list |awk '{{print $1}}' |sed 's/addr=//'|awk -F : '{{print $1}}' |sort |uniq -c |sort -nr > ./result.log".format(
            ip, pwd)
        subprocess.call(cmd, shell=True)
        for line in open('result.log','r'):
            print (line)


if __name__ == '__main__':
    redis_mo = redis_monitor()
    redis_mo.redis_client('imredis.qc.huohua.cn', 'QN!GODRt')
