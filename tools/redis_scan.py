#!/usr/bin/python
# coding:utf-8

import datetime
import time
import redis


pool = redis.ConnectionPool(host="r-2zehk7q18eqesx7ees.redis.rds.aliyuncs.com", port=6379,
                            db=13, password="AcUVeRb8lN", decode_responses=False)
r = redis.Redis(connection_pool=pool)
for k in  r.scan_iter(match=b"groupchatmember:GC_156620862737138*",count=1000):
    print (r.hget(k))
