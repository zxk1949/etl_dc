import sys
import os
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
sys.path.append('../')
from etc import MysqlPool
import time


class Check_consistance:
    def __init__(self):
        self.etl_name = 'qc_qingke_to_aishop'
        self.manage_pool=MysqlPool.Mysql("dba")
        self.get_config_sql = "select * from etl_config where etl_name ='{0}' limit 1".format(self.etl_name)
        self.config = self.manage_pool.getAll(self.get_config_sql)
        self.manage_pool.close()
        self.table_list = eval(self.config[0]['tables'])
        self.source_pool = MysqlPool.Mysql("qingke")
        self.target_pool = MysqlPool.Mysql("aishop")

    def count(self):
        time1 = time.strftime("%H-%M-%S", time.localtime())
        for t1 in self.table_list:
            sql = 'select count(*) from {0}'.format(t1)
            count1 = self.source_pool.getAll(sql)[0]['count(*)']
            print (count1)
            result = 'count1_' + time1 + '.txt'
            with open(result , "a", encoding='utf-8') as fw:
                fw.write("table:%s,%s \n" % (t1, count1))
        return result



    def main(self):
        for t1 in self.table_list:
            sql1= 'desc {0}'.format(t1)
            desc1 = self.source_pool.getAll(sql1)
            desc2 = self.target_pool.getAll(sql1)
            if desc1 != desc2:
                print ("{0}结构不一致".format(t1))
            else:
                print ("{0}结构一致".format(t1))

            sql2 = "select max(id) from {0} ".format(t1)
            max_id = self.target_pool.getAll(sql2)[0]['max(id)']
            sql3 = "select count(*) from {0} where id < {1}".format(t1, max_id)
            result1 = self.source_pool.getAll(sql3)[0]['count(*)']
            result2 = self.target_pool.getAll(sql3)[0]['count(*)']


            if result1 == result2:
                print("{0} count检测一致".format(t1))
            else:
                print("{0} count 检测不一致".format(t1))
        self.manage_pool.close()
        self.source_pool.close()
        self.target_pool.close()


class cmpFile:

    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2

    def fileExists(self):
        if os.path.exists(self.file1) and os.path.exists(self.file2):
            return True
        else:
            return False

    # 对比文件不同之处, 并返回结果
    def compare(self):
        if cmpFile(self.file1, self.file2).fileExists():
            fp1 = open(self.file1)
            fp2 = open(self.file2)
            flist1 = [i for i in fp1]
            flist2 = [x for x in fp2]

        flines1 = len(flist1)
        flines2 = len(flist2)
        if flines1 < flines2:
            flist1[flines1:flines2+1] ='' * (flines2 - flines1)
        if flines2 < flines1:
            flist2[flines2:flines1+1] =  '' * (flines1 - flines2)

        counter = 1
        cmpreses = []
        for x in zip(flist1, flist2):
            if x[0] == x[1]:
                counter +=1
                continue

            if x[0] != x[1]:
                cmpres = '%s和%s第%s行不同, 内容为: %s --> %s' %(self.file1, self.file2, counter, x[0].strip(), x[1].strip())
                cmpreses.append(cmpres)
                counter +=1
        return cmpreses




if __name__ == '__main__':
    check = Check_consistance()
    result1 = check.count()
    time.sleep(30)
    result2 = check.count()
    cmpfile = cmpFile(result1, result1)
    difflines = cmpfile.compare()
    if difflines:
        print ("qingke还有数据写入")
        for i in difflines:
            print(i, end='\n')
    else:
        print ("qingke已经无数据写入")
        check.main()


