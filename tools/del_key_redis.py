
import redis
# r = redis.Redis(host='10.89.87.121', port=6379,db=1 , password="k4tC3TmxB5DjFIZ9" ,decode_responses=True)
r = redis.Redis(host='redis-imcard.qc.huohua.cn', port=6379,db=0 , password="S7F08sZqwrVZKbzo" )

for k in r.scan_iter(match="groupinfo*" ,count=1000):
    print (k)
    #v=r.get(k)
    #with open("homework.txt", "a",encoding="utf8") as f:
    #    f.write('{0}###{1} \n'.format(k,v))
    r.delete(k)
