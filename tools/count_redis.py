# encoding=utf-8
import redis
count = 0
# r = redis.Redis(host='10.89.87.121', port=6379,db=1 , password="k4tC3TmxB5DjFIZ9" ,decode_responses=True)
r = redis.Redis(host='rediscert.qc.huohua.cn', port=6379,db=13 , password="ZgOySYlaZF55s2gz" )
# r = redis.Redis(host='10.89.87.105', port=6379,db=1 , password="ZksOi99YhTXowpfh" )
for k in r.scan_iter(match=b"account-ms:ACCOUNT_PW:*" ,count=1000):
# for k in r.scan_iter(match=b"scm:login:cache:*" ,count=1000):

    print (k)
    #v=r.get(k)
    #with open("master.log", "a",encoding="utf8") as f:
        #f.write('{0}###{1} \n'.format(k,v))
    #r.delete(k)
    count = count+1
print (count)
