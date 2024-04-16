# encoding=utf-8
# import redis
import sys,os,time
class RedisAnaly():
    def __init__(self):
        pass
    def redisAnaly(self):
        f=open("redis.log","r")

        line=f.readline().replace('\n','').replace('b\'','').replace('\'','').replace('\"','')
        count={"ip":{},"key":{},"cmd":{}}
        while line:

            liststr=line.split(" ")
            length=len(liststr)
            if(length<=4):
                line=f.readline().replace('\n','').replace('b\'','').replace('\'','').replace('\"','')
                continue
            num=liststr[2].index(':')

            #print(liststr[0],liststr[2][0:num],liststr[3],liststr[4],)
            if liststr[2][0:num] in count["ip"]:

                count["ip"][liststr[2][0:num]]=count["ip"][liststr[2][0:num]]+1
            else:
                count["ip"][liststr[2][0:num]]=1

            if liststr[3] in count["cmd"]:
                count["cmd"][liststr[3]]=count["cmd"][liststr[3]]+1
            else:
                count["cmd"][liststr[3]]=1
            if liststr[4] in count["key"]:
                count["key"][liststr[4]]=count["key"][liststr[4]]+1
            else:
                count["key"][liststr[4]]=1

            line=f.readline().replace('\n','').replace('b\'','').replace('\'','').replace('\"','')
            #time.sleep(1)
        #print(count)
        ip = sorted(count["ip"].items(), key=lambda x: x[1], reverse=True)
        key = sorted(count["key"].items(), key=lambda x: x[1], reverse=True)
        cmd = sorted(count["cmd"].items(), key=lambda x: x[1], reverse=True)
        print(ip)
        print(cmd)
        print(key)

if __name__ == '__main__':
    redisAnaly=RedisAnaly()
    redisAnaly.redisAnaly()