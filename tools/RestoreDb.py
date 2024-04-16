# encoding=utf-8
# 李晓蒙
# 2017-08-30
# mysql 数据库还原
import sys
import os
import json
import time
sys.path.append('../')
from etc import SendMail
from etc import logs
class RestoreDB():
    def __init__(self):
        sendMail= SendMail.SendMail()
        self.log=logs.Log()
        self.fileName=sys.argv[1]
        print (self.fileName)
    def ApplyLog(self):
        self.lines=os.popen('/bin/ps -ef  | grep  mysqld |grep -v auto | cut -c 9-15|xargs kill -9').readlines()
        self.lines=os.popen('cd /data0/bak/').readlines()
        self.log.writeLog.info(self.lines)
        self.lines=os.popen("/bin/rm -rf /data0/bak/temp").readlines()
        self.log.writeLog.info(self.lines)
        self.lines=os.popen("mkdir -p /data0/bak/temp").readlines()
        self.log.writeLog.info(self.lines)
        self.lines=os.popen("/usr/bin/xbstream -x -C /data0/bak/temp < {0}".format(self.fileName)).readlines()
        self.log.writeLog.info(self.lines)
        self.lines=os.popen("/usr/bin/xtrabackup --decompress --target-dir=/data0/bak/temp").readlines()
        self.log.writeLog.info(self.lines)
        self.lines=os.popen("/usr/bin/innobackupex --defaults-file=/data0/bak/temp/backup-my.cnf --apply-log /data0/bak/temp").readlines()
        self.log.writeLog.info(self.lines)
        self.lines=os.popen('/bin/chown -R mysql:mysql /data0/bak/temp/').readlines()
        self.log.writeLog.info(self.lines)
        # modify my.cnf
        f=open('/data0/bak/temp/backup-my.cnf','r')
        cnf=[]
        while 1:
            lines=f.readlines(1000)
            if not lines:
                break
            for line in lines:
                if 'innodb_data_file_path' in line:
                    cnf.append(line)
                if 'innodb_log_files_in_group' in line:
                    cnf.append(line)
                if 'innodb_log_file_size' in line:
                    cnf.append(line)

        with open('/data0/bak/temp/backup-my.cnf','w') as file:
            file.write("[mysqld]\n")
            file.write("port=3306\n")
            file.write("log-error=/data0/bak/temp/error.log\n")
        with open('/data0/bak/temp/backup-my.cnf','a') as file:
            for i in cnf:
                file.write(i)
        # run mysqld
        self.lines=os.popen("/usr/bin/nohup /usr/local/mysql/bin/mysqld_safe --defaults-file=/data0/bak/temp/backup-my.cnf --user=mysql --datadir=/data0/bak/temp/ >/dev/null 2>&1 &").readlines()
        self.log.writeLog.info(self.lines)
        self.log.writeLog.info('还原完成')
        print('还原完成')


if __name__ == '__main__':
    restoreDB=RestoreDB()
    restoreDB.ApplyLog()