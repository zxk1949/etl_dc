
import redis


r = redis.Redis(host='10.89.89.219', port=6379,db=8 , password="9ifiEKRaH0Ifk" ,decode_responses=True)
with open("rs_onlineRS_CONTAINER.txt" , "w") as f:
    f.write('')
for k in r.scan_iter(match='rs_online:RS_CONTAINER:*' ,count=1000):
    # print (k)
    # v=r.get(k)
    v=r.delete(k)
    # print (v)
    with open("rs_onlineRS_CONTAINER.txt", "a") as f:
        f.write('{0}###{1} \n'.format(k,v))