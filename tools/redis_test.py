#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis

r = redis.Redis(host='10.89.89.109', port=6379,db=6,password="crs-huzuxxpe:ray9m%nm*")
r.set('a', '1')   #添加
# a=r.hgetall('redis_all_permissions_key_hash')
# print(a)
# print(a[b'htm'].decode('utf-8','ignore'))
# print(a[b'manage'].decode('utf-8','ignore'))
# print(a[b'htp'].decode('utf-8','ignore'))
# print(a[b'crm'].decode('utf-8','ignore'))
