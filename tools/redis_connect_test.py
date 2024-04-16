import redis
import time
import datetime

Pool = redis.ConnectionPool(host='10.89.87.53', port=6379, password='ieaYZY1awQ44QkQz', db=5, max_connections=10)

while 1 :
    try:
        #短连接
        time1 = time.time()
        r = redis.Redis(host='10.89.87.53', port=6379, password='ieaYZY1awQ44QkQz',db=5)
        r.hgetall("peppacoreapi-package-CR20072534464")
        time2 = time.time()
        timediff1 =(datetime.datetime.fromtimestamp(time2) - datetime.datetime.fromtimestamp(time1)).microseconds / 1000.0
        line1 = "时间点:{0} 时间差:{1} ms".format(datetime.datetime.now(), timediff1) +'\n'
        with open('short.txt', "a", encoding='utf-8') as fw:
            fw.writelines(line1)
        if timediff1 >100:
            line_problem = "短连接 时间点:{0} 时间差:{1} ms".format(datetime.datetime.now(), timediff1) +'\n'
            with open('problem.txt', "a", encoding='utf-8') as fw:
                fw.writelines(line_problem)
        r.close()
    except Exception as E:
        line_exception = "短连接   时间点:{0}   异常:{1}".format(datetime.datetime.now(),str(E)) +'\n'
        with open('problem.txt', "a", encoding='utf-8') as fw:
            fw.writelines(line_exception)
        continue

    time.sleep(0.2)

    #连接池
    try:
        time3 = time.time()
        conn = redis.Redis(connection_pool=Pool,decode_responses = True)
        conn.hgetall("peppacoreapi-package-CR20072534464")
        time4 = time.time()
        timediff2 =(datetime.datetime.fromtimestamp(time4) - datetime.datetime.fromtimestamp(time3)).microseconds / 1000.0
        line2 = "时间点:{0} 时间差:{1} ms".format(datetime.datetime.now(), timediff2) + '\n'
        with open('long.txt', "a", encoding='utf-8') as fw:
            fw.writelines(line2)
        if timediff2 > 100:
            line_problem2 = "连接池 时间点:{0} 时间差:{1} ms".format(datetime.datetime.now(), timediff2) + '\n'
            with open('problem.txt', "a", encoding='utf-8') as fw:
                fw.writelines(line_problem)
        r.close()
    except Exception as E:
        line_exception = "连接池   时间点:{0}   异常:{1}".format(datetime.datetime.now(), str(E)) + '\n'
        with open('problem.txt', "a", encoding='utf-8') as fw:
            fw.writelines(line_exception)
        continue
    time.sleep(0.2)


