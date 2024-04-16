# encoding=utf-8
import redis
import sys,os,time
from tools import redis_bigkey
sys.path.append('../')
sys.path.append('./')
from etc import redis_config
import json
json_redis=redis_config.redis_json

redisbigkey=redis_bigkey.RedisBigkey()
class Monitor():
    def __init__(self):
        pass


    def monitor_redis(self):
        for i  in json_redis:

            print (json_redis[i]["host"],json_redis[i]["host_port"],json_redis[i]["host_password"])
            redisbigkey.main(json_redis[i]["host"],json_redis[i]["host_port"],json_redis[i]["host_password"],i ,json_redis[i]["email"])


if __name__ == '__main__':
    monitor=Monitor()
    monitor.monitor_redis()
