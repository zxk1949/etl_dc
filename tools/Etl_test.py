# encoding=utf-8
# 李晓蒙
# 2017-08-30
# 监控binlog同步指定表数据
import sys
import os
import subprocess
import json
import time
import threading
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
sys.path.append('../')
from etc import MysqlPool
import pymysql as db
from etc import config
from etc import SendMail
from tools import DateTool
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent)
from pymysqlreplication.event import (QueryEvent, RotateEvent)
sendMail = SendMail.SendMail()
from etc import logs
from tools import DingtalkApi
dingsender = DingtalkApi.Sender()
class SyncMysql:

    def __init__(self):

        # self.desc_dbLink=  db_link.DbLink( "rm-2ze5r43c891qp4ek0.mysql.rds.aliyuncs.com", 3306, "lixiaomeng", "Isolxm123", "mjn_channel_capital", 30)
        # self.desc_dbLink=  db_link.DbLink( "192.168.10.77", 6000, "lixiaomeng", "Isolxm123", "nacai4j", 30)
        # self.desc_conn=self.desc_dbLink.get_dblink()
        # self.etl_name = 'asset_general'
        self.etl_name=sys.argv[1]
        self.receiver = ['duanzexun@huohua.cn']
        self.log = logs.Log()
        self.rotateFlag = 0
        self.dtTools = DateTool.DateTool()

        self.get_config_sql="select * from etl_config where etl_name ='{0}' limit 1".format(self.etl_name)
        self.dba_pool = MysqlPool.Mysql("dba")
        self.config=self.dba_pool.getAll(self.get_config_sql)
        self.dba_pool.close()
        if  not self.config:
            print("etl_name 没找到，退出")
            exit(1)
        self.sql_thread_pool = MysqlPool.Mysql('{0}'.format(self.config[0]["desc_dbpool"]))
        # self.db = ["practice"]
        self.io_host=self.config[0]["source_host"]
        self.io_port=self.config[0]["source_port"]
        self.io_user=self.config[0]["source_user"]
        self.io_pwd=self.config[0]["source_pwd"]




    def Io_thread(self):
        global io_config

        self.io_sql=''
        # global io_config
        self.dba_pool = MysqlPool.Mysql("dba")
        self.io_config = self.dba_pool.getAll("select * from etl_config where etl_name='{0}' limit 1".format(self.etl_name))
        self.dba_pool.close()
        self.db=eval(self.io_config[0]["source_db"])
        self.rewrite_db=self.io_config[0]["rewrite_db"]
        if self.io_config[0]["tables"]=="":
            self.tables=None
        else:
            self.tables = eval(self.io_config[0]["tables"])
        line=self.io_config[0]["io_config"]
        io_config=line
        # with open('MysqlIo_test.conf', 'r', encoding='utf-8') as f:
        #     line = f.readline()
        logfile = line

        binlog = eval(line)

        stream = BinLogStreamReader(
            connection_settings= { "host": self.io_host,  "port": self.io_port,    "user": self.io_user,    "passwd": self.io_pwd , "charset": 'utf8mb4'},
            server_id=self.io_config[0]["id"], resume_stream=True,
            # skip_to_timestamp=1593306000,

            blocking=True,
            only_schemas=self.db,
            only_tables=self.tables,
            log_file=binlog['log_file'], log_pos=binlog['log_pos'],
            only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent, QueryEvent, RotateEvent]

        )

        for binlogevent in stream:

            # print(binlogevent.dump())
            # print(stream.log_file)
            # print(stream.log_pos)

            oldLogFile = logfile
            logfile = "{'log_file':'%s','log_pos':%s}" % (stream.log_file, stream.log_pos)

            self.relayFileName = stream.log_file

            if isinstance(binlogevent, RotateEvent):
                # print(binlogevent.position,binlogevent.next_binlog)
                # print(stream.log_file)
                if self.rotateFlag == 0:
                    self.rotateFlag = self.rotateFlag + 1
                else:
                    self.dicOldLogFile = eval(oldLogFile)
                    with open(self.dicOldLogFile["log_file"], "a", encoding='utf-8') as fw:
                        fw.write("#RotateEvent:%s" % (binlogevent.next_binlog))
                    # with open('MysqlIo_test.conf', 'w', encoding='utf-8') as f:
                    #     f.write(logfile)

                    io_config=logfile
                    os.popen("touch {0}".format(binlogevent.next_binlog))
                    self.rotateFlag = 0

                continue
            # 读取ddl数据
            if isinstance(binlogevent, QueryEvent):

                # self.timestamp = self.dtTools.timestamp_toString(binlogevent.timestamp)
                # print(self.timestamp)
                # print(binlogevent.query,binlogevent.schema)

                if binlogevent.query != 'BEGIN' and binlogevent.schema.decode() in self.db:
                    if self.rewrite_db:
                        # 库名重定向
                        self.schema = self.rewrite_db
                    else:

                        if isinstance(binlogevent.schema, str):
                            self.schema = binlogevent.schema
                        else:
                            self.schema = binlogevent.schema.decode()

                    # print(binlogevent.schema)
                    try:
                        # self.desc_dbLink.execute_sql(self.desc_conn,binlogevent.query)
                        self.io_sql = binlogevent.query
                        #skip triger and process
                        if "CREATE DEFINER" in  self.io_sql :
                            continue

                        self.startpos = self.io_sql.find("`")
                        self.endpos= self.io_sql.find("`.`")

                        if self.endpos>-1 and self.startpos < self.endpos:
                            self.io_sql=self.io_sql.replace( self.io_sql[self.startpos:self.endpos+2] , ' ')

                        # self.io_sql=self.io_sql.replace('\r', '').replace('\n',' ')


                        self.lines = 'use {0}  '.format(self.schema)  + '\n#position:%s\n' % (logfile)

                        with open(self.relayFileName, "a", encoding='utf-8') as fw:
                            fw.writelines(self.lines)

                        self.lines = self.io_sql + '\n#position:%s\n' % (logfile)

                        with open(self.relayFileName, "a", encoding='utf-8') as fw:
                            fw.writelines(self.lines)
                        # self.relayFileName=stream.log_file
                    except Exception as e:
                        print(e)
                        self.log.writeLog.error("  {0} 出错{1}".format(self.etl_name,str(e)))
                        msgBody = DingtalkApi.MessageBody(title="", msg= '  程序名称 {0} io线程出错 {1} '.format(self.etl_name,str(e)))
                        dingsender.send(msgBody)
                        # sendMail.Send(self.receiver, '  程序名称 {0} io线程出错'.format(self.etl_name),' 线程名称 {0},error:{1} '.format(self.etl_name,str(e)), '')
                        stream.close()
                        global exit_thread
                        exit_thread=1
            else:
                # 读取插入，更新，删除数据，并同步至目的表
                # if (isinstance(binlogevent, WriteRowsEvent) or isinstance(binlogevent, UpdateRowsEvent) or isinstance(binlogevent, DeleteRowsEvent)):
                # self.timestamp = self.dtTools.timestamp_toString(binlogevent.timestamp)
                # print(self.timestamp)
                if self.rewrite_db:
                    # 库名重定向
                    self.schema = self.rewrite_db
                else:
                    if isinstance(binlogevent.schema, str):
                        self.schema = binlogevent.schema
                    else:
                        self.schema = binlogevent.schema.decode()
                for row in binlogevent.rows:
                    event = {"schema": self.schema, "table": binlogevent.table}
                    value_set = ''
                    # where_set = ''
                    val = ''
                    col = ''

                    if isinstance(binlogevent, DeleteRowsEvent):

                        event["action"] = "delete"
                        event["values"] = dict(row["values"].items())
                        # event = dict(event.items())
                        # print(event)
                        self.io_sql = 'delete from %s.%s ' % (self.schema, event["table"]) + " where %s ='%s'" % (
                            binlogevent.primary_key, event["values"][binlogevent.primary_key])

                    elif isinstance(binlogevent, UpdateRowsEvent):
                        event["action"] = "update"
                        event["before_values"] = dict(row["before_values"].items())
                        event["after_values"] = dict(row["after_values"].items())
                        # event = dict(event.items())

                        # print(event,type(binlogevent.primary_key))
                        # print(binlogevent.primary_key,event["before_values"][binlogevent.primary_key])

                        for key, value in event["after_values"].items():
                            if isinstance(value, int):
                                value_set = value_set + "`{0}`= {1} ,".format(key, value)
                            elif value is None:
                                value_set = value_set + "`{0}`= null ,".format(key)
                            elif isinstance(value, bytes):
                                hex_value = value.hex()
                                value_set = value_set + "`{0}`=UNHEX('{1}'),".format(key, hex_value)
                            else:

                                value = db.escape_string(str(value))
                                value_set = value_set + "`{0}`='{1}',".format(key, value)


                        try:

                            self.io_sql = 'update %s.%s set ' % (self.schema, event["table"]) + value_set[0:len(
                                value_set) - 1] + ' where %s ="%s" ' % (
                                   binlogevent.primary_key, event["before_values"][binlogevent.primary_key])
                        except Exception as E:
                            msgBody = DingtalkApi.MessageBody(title="", msg= '  程序名称 {0} io线程出错 {1} '.format(self.etl_name,str(E)))
                            dingsender.send(msgBody)
                            exit_thread=1
                    elif isinstance(binlogevent, WriteRowsEvent):
                        event["action"] = "insert"
                        event["values"] = dict(row["values"].items())
                        # event = dict(event.items())
                        # print(event)
                        for key, value in event["values"].items():
                            col = col + "`{0}`,".format(key)

                            if isinstance(value, int):
                                val = val + "{0},".format(value)
                            elif value is None:
                                val = val + " null ,"
                            elif isinstance(value, bytes):
                                val = val + "UNHEX('{0}') ,".format(value.hex() )
                            else:
                                value = db.escape_string(str(value))
                                val = val + "'{0}',".format(value)
                            self.io_sql = 'insert into %s.%s (' % (self.schema, event["table"]) + col[0:len(
                                col) - 1] + ') values (' + val[0:len(val) - 1] + ')'
                    # event["timestamp"] = self.timestamp

                    self.lines = self.io_sql + '\n#position:%s\n' % (logfile)
                    with open(self.relayFileName, "a", encoding='utf-8') as fw:
                        fw.writelines(self.lines)
                io_config=logfile



        stream.close()

    def sql_thread(self):
        global sql_config
        global exit_thread

        self.sql_num = 1
        self.sql=''
        # global sql_config
        self.dba_pool = MysqlPool.Mysql("dba")
        self.sql_config=self.dba_pool.getAll("select * from etl_config where etl_name='{0}' limit 1".format(self.etl_name))
        self.dba_pool.close()
        self.lineOffset=eval(self.io_config[0]["sql_config"])
        sql_config=self.lineOffset
        # with open("MysqlSql_test.conf", 'r',encoding="utf-8") as f:
        #     self.lineOffset = eval(f.readline())

        if not os.path.exists(self.lineOffset['log_file']):
            os.popen("touch {0}".format(self.lineOffset['log_file']))
            time.sleep(0.5)
        file = open(self.lineOffset['log_file'], 'r', encoding="utf8")
        file.seek(self.lineOffset['log_pointer'], 0)

        while 1:
            try:
                self.line = file.readline()
                if self.line == '':
                    time.sleep(1)
                    continue
                if self.line[0:12] == "#RotateEvent":

                    file.close()
                    self.logFile = self.line[13:]
                    # print(self.logFile)
                    while 1:
                        if os.path.exists(self.logFile):

                            file = open(self.logFile, 'r', encoding="utf8")

                            break
                        else:
                            # print('文件不存在，睡眠1秒')
                            self.log.writeLog.warning('%s文件不存在，睡眠1秒' % (self.logFile))
                            os.popen("touch {0}".format(self.logFile))
                            time.sleep(1)
                    # time.sleep(10)
                    continue
            except Exception as E:
                self.writeLine = "{'log_pointer':%s,'log_file':'%s','log_pos':%s}" % (
                    str(file.tell()), self.logFile['log_file'], self.logFile['log_pos'])
                print(self.sql)
                print(str(E))
                self.log.writeLog.error('etl %s Open relay log 出错%s ,%s' % (self.etl_name, str(E), self.sql))
                msgBody = DingtalkApi.MessageBody(title="", msg='etl {0} open  relay log 出错{1}  ,{2},position :{3}'.format(
                    self.etl_name, str(E), self.sql, self.writeLine))
                dingsender.send(msgBody)
                self.sql=''
                time.sleep(5)

                # exit_thread=1
                break

            if self.line[0:9] == "#position":

                try:
                    self.logFile = eval(self.line[10:])
                    self.writeLine = '''{'log_pointer':%s,'log_file':'%s','log_pos':%s}''' % (
                    str(file.tell()), self.logFile['log_file'], self.logFile['log_pos'])
                    # print(self.sql)
                    sql_config = self.writeLine
                except Exception as E:
                    msgBody = DingtalkApi.MessageBody(title="",msg='etl {0}  str to dict 出错{1}   ,line {2} ,position :{3}'.format(self.etl_name, str(E), self.line, self.writeLine))
                    dingsender.send(msgBody)




                try:



                    self.result = self.sql_thread_pool.update(self.sql)


                except Exception as e:
                    if '1062' in str(e) and 'Duplicate' in str(e):
                        self.sql = ''

                        # self.writeLine = "{'log_pointer':%s,'log_file':'%s','log_pos':%s}" % ( str(file.tell()), self.logFile['log_file'], self.logFile['log_pos'])
                        # with open("MysqlSql_test.conf", "w", encoding="utf-8") as f:
                        #     f.write(self.writeLine)
                        continue
                    else:
                        # self.writeLine = "{'log_pointer':%s,'log_file':'%s','log_pos':%s}" % (str(file.tell()), self.logFile['log_file'], self.logFile['log_pos'])
                        print(self.sql)
                        print(str(e))
                        # self.log.writeLog.error('etl {0} 程序出错{1} ,{2}'.format(self.etl_name,str(e), self.sql))
                        self.log.writeLog.error('etl %s  relay log 出错%s,line : %s ,%s'% (self.etl_name,str(e),self.line, self.sql))
                        msgBody = DingtalkApi.MessageBody(title="", msg='etl {0}  relay log 出错{1}  ,{2},position :{3}'.format(self.etl_name,str(e), self.sql,self.writeLine))
                        dingsender.send(msgBody)
                        # self.sendMail = SendMail.SendMail()
                        # self.sendMail.Send(self.receiver, 'etl {0} relay log 出错'.format(self.etl_name),'线程名称 {0},error:{1} ,sql: {2},{3}'.format(self.etl_name,str(e), self.sql,self.writeLine), '')
                        # exit_thread=1
                        self.sql=""
                        time.sleep(5)
                        break


                self.sql = ''
            else:
                self.sql = self.sql + self.line
    def save_config(self):
        global sql_config
        global io_config
        self.dba_save_pool = MysqlPool.Mysql("dba")
        while 1:
            if sql_config != '' and io_config != '':
                self.config_sql ='''update etl_config set sql_config="{0}" ,io_config="{1}" where etl_name="{2}" '''.format(sql_config, io_config, self.etl_name)
                # print(self.config_sql)
                try:
                    self.dba_save_pool.update(self.config_sql)
                except Exception as E:
                    msgBody = DingtalkApi.MessageBody(title="",  msg='etl {0} save config 出错{1}  ,{2} '.format(self.etl_name,str(E), self.config_sql))
                    dingsender.send(msgBody)


            time.sleep(5)
    def send_Mail(self,receiver,sub,content,atta):
        sendMail = SendMail.SendMail()
        sendMail.Send(receiver, sub, content,atta)

    def init_data(self):



        if self.config[0]["is_init_data"] == 1:
            __pool = PooledDB(creator=pymysql, mincached=2, maxcached=30,
                              host=self.config[0]["source_host"], port=self.config[0]["source_port"], user=self.config[0]["source_user"],
                              passwd=self.config[0]["source_pwd"],
                              db="mysql", charset='utf8mb4', cursorclass=DictCursor, autocommit=1)
            self.conn=__pool.connection()
            self.cur=self.conn.cursor()
            self.cur.execute("show master status")
            self.binlog=self.cur.fetchall()
            self.cur.close()
            self.conn.close()
            self.io_config="{{'log_file':'{0}','log_pos':{1}}}".format(self.binlog[0]["File"],self.binlog[0]["Position"])
            self.sql_config="{{'log_pointer': 0,'log_file':'{0}','log_pos':{1}}}".format(self.binlog[0]["File"],self.binlog[0]["Position"])
            self.init_shell=" /usr/local/mysql/bin/mysqldump -h{source_host} -P{source_port}  -u{source_user} -p{source_pwd}   --max_allowed_packet=64M  --net_buffer_length=4M " \
                            "--set-gtid-purged=OFF --single-transaction --databases dbname_position --tables tablename_postion  " \
                            "|/usr/local/mysql/bin/mysql -h{desc_host} -P{desc_port} -u{desc_user} -p{desc_pwd} {rewrite_db}".format(**self.config[0])
            self.dbname= " ".join(eval(self.config[0]["source_db"] ))
            self.tables=" ".join(eval(self.config[0]["tables"] ))

            self.exec_shell=self.init_shell.replace("dbname_position",self.dbname).replace("tablename_postion" ,self.tables)

            self.result=''
            self.resutl=subprocess.Popen(self.exec_shell, shell=True , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # self.result=os.popen(self.exec_shell)

            print('########',self.result ,'##')
            if self.result.replace("mysqldump: [Warning] Using a password on the command line interface can be insecure.",'').replace("mysql: [Warning] Using a password on the command line interface can be insecure.",'') =='':
                self.config_sql='''update etl_config set io_config="{0}" ,sql_config="{1}" , is_init_data=0 where etl_name="{2}" '''.format(self.io_config,self.sql_config,self.etl_name)
                self.dba_pool = MysqlPool.Mysql("dba")
                self.dba_pool.update(self.config_sql)
                self.dba_pool.close()
                print("初始化完成")
            else:
                self.log.writeLog.error('{0}全量初始化出错{1}'.format(self.etl_name,self.result))
                msgBody = DingtalkApi.MessageBody(title="", msg='{0}全量初始化出错 {1}'.format(self.etl_name,self.result) )
                dingsender.send(msgBody)
                exit(1)

if __name__ == '__main__':
    syncMysql = SyncMysql()
    syncMysql.init_data()
    global sql_config
    global io_config
    global exit_thread
    exit_thread=0
    sql_config=''
    io_config=''

    t1 =threading.Thread(target=syncMysql.Io_thread )
    t1.setName('io_thread')
    t1.setDaemon(True)
    t1.start()
    #
    time.sleep(1)
    t2 =threading.Thread(target=syncMysql.sql_thread)
    t2.setName("sql_thread")
    t2.setDaemon(True)
    t2.start()
    #
    t3 = threading.Thread(target=syncMysql.save_config)
    t3.setName("save_config")
    t3.setDaemon(True)
    t3.start()
    while 1 :
        # print(t1.getName(), t1.isAlive())
        # print(t2.getName(),t2.isAlive())
        # print(t3.getName(), t3.isAlive())
        if not t1.is_alive() :
            syncMysql.log.writeLog.error('  {0} 线程出错'.format(t1.getName()))
            msgBody = DingtalkApi.MessageBody(title="", msg='  {0} 线程出错 etl_name:{1} '.format(t1.getName(),syncMysql.etl_name))
            dingsender.send(msgBody)
            syncMysql.send_Mail(syncMysql.receiver, '  {0} 线程出错  etl_name:{1}'.format(t1.getName() ,syncMysql.etl_name), '  {0}线程出错 etl_name:{1} '.format(t1.getName() ,syncMysql.etl_name), '')

            t1 = threading.Thread(target=syncMysql.Io_thread)
            t1.setName('io_thread')
            t1.setDaemon(True)
            t1.start()
        if not t2.is_alive() :
            syncMysql.log.writeLog.error('  {0} 线程出错'.format(t2.getName()))
            msgBody = DingtalkApi.MessageBody(title="", msg='  {0} 线程出错 etl_name:{1}'.format(t2.getName(),syncMysql.etl_name))
            dingsender.send(msgBody)
            syncMysql.send_Mail(syncMysql.receiver, '  {0} 线程出错,etl_name:{1}'.format(t2.getName(),syncMysql.etl_name), '  {0}线程出错 etl_name:{1} '.format(t1.getName(),syncMysql.etl_name), '')
            t2 = threading.Thread(target=syncMysql.sql_thread)
            t2.setName("sql_thread")
            t2.setDaemon(True)
            t2.start()

        if not t3.is_alive() :
            syncMysql.log.writeLog.error('  {0} 线程出错 etl_name:{1} '.format(t3.getName(),syncMysql.etl_name))
            msgBody = DingtalkApi.MessageBody(title="", msg='  {0} 线程出错'.format(t3.getName()))
            dingsender.send(msgBody)
            syncMysql.send_Mail(syncMysql.receiver, '  {0} 线程出错 etl_name:{1} '.format(t3.getName(),syncMysql.etl_name), '  {0}线程出错  etl_name:{1}'.format(t1.getName() ,syncMysql
                                                                                                                                                         .etl_name), '')
            t3 = threading.Thread(target=syncMysql.save_config)
            t3.setName("save_config")
            t3.setDaemon(True)
            t3.start()
        if exit_thread==1:
            exit(0)

        # print(io_config,sql_config)
        time.sleep(4)
