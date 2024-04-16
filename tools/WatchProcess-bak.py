# encoding=utf-8
# 李晓蒙
# 2017-08-30
#数据同步
import logging
import os
import sys
sys.path.append('.')
sys.path.append('../')
from etc import MysqlPool
from etc import SendMail
from etc import logs
sendMail= SendMail.SendMail()
from tools import DingtalkApi
dingsender = DingtalkApi.Sender()
class WATCH:
    def __init__(self):
        self.log=logs.Log()
        self.receiver=['lixiaomeng@huohua.cn']
    def watch_process(self):
        self.dba_db = MysqlPool.Mysql('dba')

        rows=self.dba_db.getAll('select id,process_name,run_command,auto_run from `dba`.watch_process where is_del=2 ')
        info=[]
        for row in rows:
            info=os.popen('ps aux | grep "' + '{0}'.format(row["process_name"]) + '" | grep -v grep').readlines()
            # print(info)


            if len(info)==0 :


                self.log.writeLog.error('%s程序退出'%(row["process_name"]))
                msgBody = DingtalkApi.MessageBody('{0} 程序退出，请检查 '.format(row["process_name"]))
                dingsender.send(msgBody)
                if   row["auto_run"]==1 :


                    rs=os.popen(row["run_command"])
                    msgBody = DingtalkApi.MessageBody('{0}  将尝试拉起。  '.format(row["process_name"] ))
                    dingsender.send(msgBody)
                    self.log.writeLog.info('{0} 将尝试拉起  '.format(row["process_name"] ))
                    print(111)

                # sendMail.Send(self.receiver,'%s程序出错'%(row["process_name"]),'%s程序退出'%(row["process_name"]),'')
            if len(info)>1:
                lines=''
                self.flag=0
                for line in info:

                    lines=lines+line+'\n'
                    if 'more' in line or 'tail' in line:
                        self.flag=1
                if self.flag==0:
                    self.dba_db.update('update `dba`.watch_process set remark="检测到多个进程，请检查" where id=%s'%(row["id"]) )
                    self.log.writeLog.error('检测到多个进程，请检查{0}\n ; 进程信息：\n {1}'.format(row["process_name"],lines)  )

                    msgBody=DingtalkApi.MessageBody('检测到多个进程，请检查{0}\n ; 进程信息：\n {1}'.format(row["process_name"],lines)  )
                    dingsender.send(msgBody)

            if len(info)==1:
                continue
                # self.log.writeLog.info('{0}运行中'.format(row["process_name"]))




if __name__ == '__main__':
    watch=WATCH()
    watch.watch_process()



