# encoding=utf-8
import sys
import redis
sys.path.append('../')
sys.path.append('./')
from etc import SendMail
class RedisBigkey():
    def __init__(self):
        self.receiver=['lixiaomeng@huohua.cn']
    def check_big_key(self,r, k,db_num):

        num=0
        bigKey = False
        length = 0
        try:
            type = r.type(k)
            if type == "string":
                length = r.strlen(k)
            elif type == "hash":
                length = r.hlen(k)
            elif type == "list":
                length = r.llen(k)
            elif type == "set":
                length = r.scard(k)
            elif type == "zset":
                length = r.zcard(k)
        except:
            return
        if type == "string" and  length > 204800:
            bigKey = True
        if type == "hash" and  length > 20000:
            bigKey = True
        if type == "list" and  length > 100000:
            bigKey = True
        if type == "set" and  length > 100000:
            bigKey = True
        if type == "zset" and  length > 100000:
            bigKey = True


        # print (db_num, k, type, length)
        if bigKey:
            print (db_num, k, type, length)
            with open("bigkey_%s.txt"%db_num,"a") as f:
                f.writelines('db_num:%s'%db_num+'   '+ str(k)+'   '+ str(type)+'   '+ str(length)+'\n')
            # print (db, k, type, length)
            return 1
        else:
            return 0



    def find_big_key_normal(self,redis_name,db_host, db_port, db_password, db_num,email):
        r = redis.StrictRedis(host=db_host, port=db_port, password=db_password, db=db_num)
        sumnum=0

        with open("bigkey_%s.txt"%db_num, "w") as f:
            f.write('')
        for k in r.scan_iter(count=1000):
            num=self.check_big_key(r, k,db_num)
            sumnum=sumnum+num
        if sumnum>0:


            self.sendMail = SendMail.SendMail()
            self.sendMail.Send(email, 'redis big key 告警', 'redis name :  {3}  \nredis ip :{0} \n db_num :  {1} \n big key num :  {2} \n 详情见附件'.format(db_host,db_num,  sumnum,redis_name), "bigkey_%s.txt"%db_num)


    def find_big_key_sharding(self,redis_name,db_host, db_port, db_password, db_num, nodecount,email):
        r = redis.StrictRedis(host=db_host, port=db_port, password=db_password, db=db_num)
        cursor = 0
        for node in range(0, nodecount):
            while True:
                iscan = r.execute_command("iscan", str(node), str(cursor), "count", "1000")
                for k in iscan[1]:
                    self.check_big_key(r, k)
                cursor = iscan[0]
                print (cursor, db, node, len(iscan[1]))
                if cursor == "0":
                    break;
    def main(self,db_host,db_port,db_password,redis_name,email):

        r = redis.StrictRedis(host=db_host, port=db_port, password=db_password)
        # nodecount = r.info()['nodecount']
        nodecount = 1
        keyspace_info = r.info("keyspace")
        redisBigkey = RedisBigkey()
        for db in keyspace_info:
            print ('check ', db, ' ', keyspace_info[db])
            if nodecount > 1:
                redisBigkey.find_big_key_sharding(redis_name,db_host, db_port, db_password, db.replace("db", ""), nodecount,email)
            else:
                redisBigkey.find_big_key_normal(redis_name,db_host, db_port, db_password, db.replace("db", ""),email)


if  __name__ == '__main__':

    db_host = '10.89.89.109'
    db_port = 6379
    db_password = 'crs-huzuxxpe:ray9m%nm*'
    r = redis.StrictRedis(host=db_host, port=int(db_port), password=db_password)
    # nodecount = r.info()['nodecount']
    nodecount=1
    keyspace_info = r.info("keyspace")
    redisBigkey=RedisBigkey()
    for db in keyspace_info:
        print ('check ', db, ' ', keyspace_info[db])
        if nodecount > 1:
            redisBigkey.find_big_key_sharding(db_host, db_port, db_password, db.replace("db", ""), nodecount)
        else:
            redisBigkey.find_big_key_normal(db_host, db_port, db_password, db.replace("db", ""))