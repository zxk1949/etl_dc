# encoding=utf-8
# 2024-04-11
# zxk
#修复了不同库名称之间的同步，ddl 操作，以及特殊字符集的问题
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
from tools import DingtalkApi_1

dingsender = DingtalkApi_1.Sender()

class SyncMysql:

    def __init__(self):

        self.etl_name = sys.argv[1]
        self.receiver = ['xiaokang.zhang@sparkedu.com']
        self.log = logs.Log()
        self.rotateFlag = 0
        self.dtTools = DateTool.DateTool()

        self.get_config_sql = "select * from etl_config where etl_name ='{0}' limit 1".format(self.etl_name)
        self.dba_pool = MysqlPool.Mysql("dba")
        self.config = self.dba_pool.getAll(self.get_config_sql)
        self.dba_pool.close()
        if not self.config:
            print("etl_name 没找到，退出")
            exit(1)
        
        self.io_host = self.config[0]["source_host"]
        self.io_port = self.config[0]["source_port"]
        self.io_user = self.config[0]["source_user"]
        self.io_pwd = self.config[0]["source_pwd"]
        self.relay_log_dir = self.config[0]["relay_log_dir"]

    def Io_thread(self):
        global io_config

        self.tables = []
        self.tables_new=[]

        self.io_sql = ''
        # global io_config
        self.dba_pool = MysqlPool.Mysql("dba")

        self.io_config = self.dba_pool.getAll(
            "select * from etl_config where etl_name='{0}' limit 1".format(self.etl_name))
        self.dba_pool.close()

        self.db = eval(self.io_config[0]["source_db"])
        self.rewrite_db = self.io_config[0]["rewrite_db"]

        if self.io_config[0]["tables"] == "":
            self.tables = None
        else:

            self.tables_result = eval(self.io_config[0]["tables"])

            for table in self.tables_result:
                self.tables.append(table)
                self.tables_new.append('_' + table + "_new")
                

        line = self.io_config[0]["io_config"]
        io_config = line
        
        logfile = line

        binlog = eval(line)
        if binlog['log_pos'] == 4:
            
            with open(self.relay_log_dir + binlog['log_file'], "w", encoding='utf-8') as fw:
                fw.writelines('')

        stream = BinLogStreamReader(
            connection_settings={"host": self.io_host, "port": self.io_port, "user": self.io_user,
                                 "passwd": self.io_pwd, "charset": 'utf8mb4'},
            server_id=self.io_config[0]["id"], resume_stream=True,
            # skip_to_timestamp=1593306000,

            blocking=True,
            only_schemas=self.db,
            only_tables=self.tables,
            log_file=binlog['log_file'], log_pos=binlog['log_pos'],
            only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent, QueryEvent, RotateEvent]

        )

        for binlogevent in stream:

            oldLogFile = logfile
            logfile = "{'log_file':'%s','log_pos':%s}" % (stream.log_file, stream.log_pos)

            self.relayFileName = stream.log_file

            if isinstance(binlogevent, RotateEvent):
               
                self.dicOldLogFile = eval(oldLogFile)
                if self.dicOldLogFile["log_file"] in binlogevent.next_binlog:
                   
                    continue
                else:
                    with open(self.relay_log_dir + self.dicOldLogFile["log_file"], "a", encoding='utf-8') as fw:
                        fw.write("#RotateEvent:%s" % (binlogevent.next_binlog))

                    io_config = logfile
                    with open(self.relay_log_dir + binlogevent.next_binlog, "w", encoding='utf-8') as fw:
                        fw.writelines('')

                continue
            # 读取ddl数据
            if isinstance(binlogevent, QueryEvent):

                if binlogevent.query != 'BEGIN' and binlogevent.schema.decode() in self.db:

                    if self.rewrite_db:
                        # 库名重定向
                        self.schema = self.rewrite_db
                    else:

                        if isinstance(binlogevent.schema, str):
                            self.schema = binlogevent.schema
                        else:
                            self.schema = binlogevent.schema.decode()

                    try:
                        self.io_sql = binlogevent.query
                        # skip triger and process
                        if "CREATE DEFINER" in self.io_sql or "ANALYZE TABLE" in self.io_sql or "DROP TRIGGER" in self.io_sql or "CREATE DATABASE" in self.io_sql:
                            continue

                        self.io_sql=self.io_sql.lower()
                        # print(self.io_sql,'#######')
                        if 'create table' in self.io_sql and '_new' in self.io_sql:

                            continue
                        if 'rename' in self.io_sql and '_new' in self.io_sql and '_old' in self.io_sql:

                            continue
                        if 'drop' in self.io_sql and '_old' in self.io_sql:

                            continue
                        if 'alter' in self.io_sql and '_new' in self.io_sql:

                            if self.tables is None:
                                self.io_sql = self.io_sql.replace('.`_','.').replace(' `_',' ').replace('_new` ',' ')
                                if binlogevent.schema.decode()!=self.schema:
                                    self.io_sql = self.io_sql.replace('`'+binlogevent.schema.decode()+'`.',self.schema+'.').replace(self.schema+'.',self.schema+'.')

                            else :

                                for table in self.tables_new:
                                    
                                    self.table_lower = table.lower()
                                    if ' ' + self.table_lower + ' ' in self.io_sql or '`' + self.table_lower + '`' in self.io_sql:
                                        self.io_sql=self.io_sql.replace(self.table_lower,table[1:].replace("_new",''))
                                        
                                    if binlogevent.schema.decode()!=self.schema:
                                         self.io_sql = self.io_sql.replace('`'+binlogevent.schema.decode()+'`.',self.schema+'.').replace(self.schema+'.',self.schema+'.')
                            self.io_sql = self.io_sql

                        else:                        
                            self.io_sql = self.io_sql.replace('`' + binlogevent.schema.decode() + '`.',self.schema + '.').replace(binlogevent.schema.decode() + '.',self.schema + '.')
                        
                        #self.io_sql = self.io_sql.replace('`'+binlogevent.schema.decode()+'`.',self.schema+'.').replace(binlogevent.schema.decode()+'.',self.schema+'.')
                        #self.io_sql = self.io_sql

                        self.continue_flag = 0
                        if self.tables is None :

                            self.lines = self.io_sql + '\n#position:%s\n' % (logfile)
                            print(self.lines)
                            self.continue_flag = 1

                        else:
                            for t in self.tables_new :
                                if ' `' + t + '` ' in self.io_sql or ' ' + t + ' ' in self.io_sql or '.`' + t + '` ' in self.io_sql or '.' + t + ' ' in self.io_sql:
                                    self.lines = self.io_sql + '\n#position:%s\n' % (logfile)
                                    self.continue_flag = 1
                                    break
                            for t in self.tables:
                                if ' `' + t + '` ' in self.io_sql or ' ' + t + ' ' in self.io_sql or '.`' + t + '` ' in self.io_sql or '.' + t + ' ' in self.io_sql:
                                    self.lines = self.io_sql + '\n#position:%s\n' % (logfile)
                                    self.continue_flag = 1
                                    break
                        if self.continue_flag == 0:
                            continue

                        with open(self.relay_log_dir + self.relayFileName, "a", encoding='utf-8') as fw:
                            fw.writelines(self.lines)
                        io_config = logfile
                    except Exception as e:
                        print(e)
                        self.log.writeLog.error("  {0} 出错{1}".format(self.etl_name, str(e)))
                        msgBody='程序名称 {0} io线程出错 {1} '.format(self.etl_name, str(e))
                        dingsender.send(msgBody)
                        stream.close()
                        global exit_thread
                        exit_thread = 1
            else:
                # 读取插入，更新，删除数据，并同步至目的表
                # if (isinstance(binlogevent, WriteRowsEvent) or isinstance(binlogevent, UpdateRowsEvent) or isinstance(binlogevent, DeleteRowsEvent)):
                self.timestamp = self.dtTools.timestamp_toString(binlogevent.timestamp)
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

                    if event['table'][0:1] == '_' and event['table'][len(event['table']) -4 :] == '_new':
                        continue

                    if isinstance(binlogevent, DeleteRowsEvent):

                        event["action"] = "delete"
                        event["values"] = dict(row["values"].items())
                        event["timestamp"] = self.timestamp
                        if isinstance(binlogevent.primary_key, tuple):
                            for i in binlogevent.primary_key:
                                self.pri_where = self.pri_where + ' {0}="{1}" and'.format(i, event["before_values"][i])

                            self.io_sql = 'delete from %s.%s ' % (self.schema, event["table"]) + " where %s " % (
                            self.pri_where[:-3])
                        else:
                            self.io_sql = 'delete from %s.%s ' % (self.schema, event["table"]) + " where %s ='%s'" % (
                                binlogevent.primary_key, event["values"][binlogevent.primary_key])

                    elif isinstance(binlogevent, UpdateRowsEvent):
                        # if binlogevent.table =='crm_cust_leads_redundancy':
                            # print(row ,'####')
                        event["action"] = "update"
                        event["before_values"] = dict(row["before_values"].items())
                        event["after_values"] = dict(row["after_values"].items())


                        for key, value in event["after_values"].items():
                            if isinstance(value, int) :
                                value_set = value_set + "`{0}`= '{1}' ,".format(key, value)
                            elif value is None:
                                value_set = value_set + "`{0}`= null ,".format(key)
                            elif isinstance(value, bytes):
                                if value in (b'1', b'0'):
                                    value_set = value_set + "`{0}`=b'{1}',".format(key, int(value))
                                else:
                                    hex_value = value.hex()
                                    value_set = value_set + "`{0}`=UNHEX('{1}'),".format(key, hex_value)
                            elif isinstance(value, str) : #and value.isdigit():
                                value = db.escape_string(str(value))
                                value_set = value_set + "`{0}`='{1}',".format(key, value)

                            else:

                                value = db.escape_string(str(value))
                                value_set = value_set + "`{0}`='{1}',".format(key, value)

                        try:
                            self.pri_where = ''
                            if isinstance(binlogevent.primary_key, tuple):
                                for i in binlogevent.primary_key:
                                    self.pri_where = self.pri_where + ' {0}="{1}" and'.format(i,
                                                                                              event["before_values"][i])
                                    # print(self.pri_where)

                                self.io_sql = 'update %s.%s set ' % (self.schema, event["table"]) + value_set[0:len(
                                    value_set) - 1] + ' where %s ' % (self.pri_where[:-3])


                            else:

                                self.io_sql = 'update %s.%s set ' % (self.schema, event["table"]) + value_set[0:len(
                                    value_set) - 1] + ' where %s ="%s" ' % (
                                                  binlogevent.primary_key,
                                                  event["before_values"][binlogevent.primary_key])

                            # print(self.io_sql)


                        except Exception as E:
                            print(E)
                            msgBody='程序名称 {0} io线程出错 {1}, event:{2} '.format(self.etl_name, str(E), str(event))
                            dingsender.send(msgBody)
                            exit_thread = 1
                    elif isinstance(binlogevent, WriteRowsEvent):
                        event["action"] = "insert"
                        event["values"] = dict(row["values"].items())
                        for key, value in event["values"].items():
                            col = col + "`{0}`,".format(key)

                            if isinstance(value, int)  :
                                val = val + "'{0}',".format(value)
                            elif value is None:
                                val = val + " null ,"
                            elif isinstance(value, bytes):
                                if value in (b'1' , b'0'):

                                    val = val + "b'{0}' ,".format(int(value))

                                else:
                                    val = val + "UNHEX('{0}') ,".format(value.hex())
                            else:
                                value = db.escape_string(str(value))
                                val = val + "'{0}',".format(value)
                            self.io_sql = 'insert ignore into %s.%s (' % (self.schema, event["table"]) + col[0:len(
                                col) - 1] + ') values (' + val[0:len(val) - 1] + ')'

                    self.lines = self.io_sql + '\n#position:%s\n' % (logfile)
                    with open(self.relay_log_dir + self.relayFileName, "a", encoding='utf-8') as fw:
                        fw.writelines(self.lines)
                io_config = logfile

        stream.close()

    def sql_thread(self):
        global sql_config
        global exit_thread

        self.sql_num = 1
        self.sql = ''
        self.null_num=1
        # global sql_config
        self.dba_pool_sql = MysqlPool.Mysql("dba")
        self.sql_thread_pool = MysqlPool.Mysql('{0}'.format(self.config[0]["desc_dbpool"]))
        if self.config[0]["rewrite_db"] !='':
            self.use_sql= 'use {0} '.format(self.config[0]["rewrite_db"])
            print(self.use_sql)
        self.sql_thread_pool.update(self.use_sql)
        self.sql = "select * from etl_config where etl_name='{0}' limit 1".format(self.etl_name)

        self.sql_config = self.dba_pool_sql.getAll(self.sql)

        self.sql = ''

        self.dba_pool_sql.close()
        self.lineOffset = eval(self.sql_config[0]["sql_config"])

        sql_config = self.lineOffset
        self.log.writeLog.info('etl 线程 %s 启动 ，config :%s  ' % (self.etl_name, self.sql_config[0]["sql_config"]))

        if not os.path.exists(self.relay_log_dir + self.lineOffset['log_file']):
            with open(self.relay_log_dir + self.lineOffset['log_file'], "w", encoding='utf-8') as fw:
                fw.writelines('')

            time.sleep(0.5)
        file = open(self.relay_log_dir + self.lineOffset['log_file'], 'rb')
        file.seek(self.lineOffset['log_pointer'], 0)
        self.logFile=self.lineOffset

        while 1:

            try:
                self.line = file.readline()

                if not self.line:
                    time.sleep(1)
                    # print('sleep 1')
                    self.null_num = self.null_num + 1

                    if self.null_num%10000==0:
                        self.log.writeLog.info(
                            'name:{0} , self.line 空，sleep 1 秒 {1}'.format(self.etl_name, self.logFile))

                        self.null_num=1

                    continue
                else:
                    self.null_num=1
                if self.line[0:12] == b"#RotateEvent" or self.line[0:12] == "#RotateEvent":

                    file.close()
                    self.logFile = bytes.decode(self.line[13:]).replace('\n', '')

                    while 1:

                        if os.path.exists(self.relay_log_dir + self.logFile):

                            file = open(self.relay_log_dir + self.logFile, 'rb')

                            break
                        else:
                            self.log.writeLog.warning('%s文件不存在，睡眠1秒' % (self.logFile))
                            time.sleep(1)
                    continue
            except Exception as E:
                self.writeLine = "{'log_pointer':%s,'log_file':'%s','log_pos':%s}" % (
                    str(file.tell()), self.logFile['log_file'], self.logFile['log_pos'])
                print(self.sql)
                print(str(E))
                self.log.writeLog.error('etl %s Open relay log 出错%s ,%s' % (self.etl_name, str(E), self.sql))
                msgBody='etl {0} open  relay log 出错{1}  ,{2},position :{3}'.format(self.etl_name, str(E), self.sql, self.writeLine)
                dingsender.send(msgBody)
                self.sql = ''
                time.sleep(5)

                break

            if self.line[0:9] == b"#position":

                try:
                    self.logFile = eval(self.line[10:])
                    self.writeLine = '''{'log_pointer':%s,'log_file':'%s','log_pos':%s}''' % (
                        str(file.tell()), self.logFile['log_file'], self.logFile['log_pos'])
                except Exception as E:
                    msgBody='etl {0}  str to dict 出错{1}   ,line {2} ,position :{3}'.format(self.etl_name, str(E), self.line, self.writeLine)
                    dingsender.send(msgBody)
                    break

                try:

                    self.result = self.sql_thread_pool.update(self.sql)

                    sql_config = self.writeLine



                except Exception as e:

                    if ('1062' in str(e) and 'Duplicate' in str(e)) or ('1061' in str(e) and 'Duplicate' in str(e)) \
                            or ('1050' in str(e) and 'already exists' in str(e)):
                        # print(str(e))
                        self.sql = ''

                        continue
                    else:
                        print(self.sql)
                        print(str(e))
                        self.log.writeLog.error(
                            'etl %s  relay log 出错%s,line : %s ,sql: %s' % (self.etl_name, str(e), self.line, self.sql))
                        msgBody='etl {0}  relay log 出错{1}  ,{2},position :{3}'.format(self.etl_name, str(e), self.sql, sql_config)
                        dingsender.send(msgBody)
                        self.sql = ""
                        self.sql_thread_pool.close()
                        time.sleep(60)
                        break

                self.sql = ''
            else:
                self.sql = self.sql + bytes.decode(self.line)

    def save_config(self):
        global sql_config
        global io_config
        self.dba_save_pool = MysqlPool.Mysql("dba")
        while 1:

            if sql_config != '' and io_config != '':
                self.config_sql = '''update etl_config set sql_config="{0}" ,io_config="{1}" where etl_name="{2}" '''.format(
                    sql_config, io_config, self.etl_name)
                # print(self.config_sql)
                try:
                    self.dba_save_pool.update(self.config_sql)
                    self.dba_save_pool.end("commit")
                except Exception as E:
                    msgBody='etl {0} save config 出错{1}  ,{2} '.format(self.etl_name,str(E),self.config_sql)
                    dingsender.send(msgBody)

            time.sleep(5)

    def send_Mail(self, receiver, sub, content, atta):
        sendMail = SendMail.SendMail()
        sendMail.Send(receiver, sub, content, atta)

    def check_process(self, etl_name):

        self.info = os.popen('ps aux | grep "' + '{0}'.format(etl_name) + '" | grep -v grep').readlines()
        if len(self.info) > 1:
            print("程序已在运行，请勿重复运行。进程信息如下：\n{0}".format(self.info[0]))
            exit(1)

    def reset_binlog(self, etl_name, ioconfig, sqlconfig):
        global sql_config
        global io_config
        global exit_thread
        exit_thread = 0
        sql_config = sqlconfig
        io_config = ioconfig
        self.config_sql = '''update etl_config set io_config="{0}" ,sql_config="{1}" , is_init_data=0 where etl_name="{2}" '''.format(
            io_config, sql_config, etl_name)
        print(self.config_sql)
        self.dba_pool = MysqlPool.Mysql("dba")
        self.dba_pool.update(self.config_sql)
        self.dba_pool.end()
        self.dba_pool.close()
        print(111)

    def init_data(self):
        global sql_config
        global io_config

        if self.config[0]["is_init_data"] == 1:
            __pool = PooledDB(creator=pymysql, mincached=2, maxcached=30,
                              host=self.config[0]["source_host"], port=self.config[0]["source_port"],
                              user=self.config[0]["source_user"],
                              passwd=self.config[0]["source_pwd"],
                              db="mysql", charset='utf8mb4', cursorclass=DictCursor, autocommit=1)
            self.conn = __pool.connection()
            self.cur = self.conn.cursor()
            self.cur.execute("show master status")
            self.binlog = self.cur.fetchall()
            print(self.binlog)
            self.cur.close()
            self.conn.close()
            self.io_config = "{'log_file':'%s','log_pos':%s,'table':''}"%(self.binlog[0]["File"],
                                                                         self.binlog[0]["Position"])
            self.sql_config = "{'log_pointer': 0,'log_file':'%s','log_pos':%s,'table':''}"%(self.binlog[0]["File"],
                                                                                           self.binlog[0]["Position"])
            sql_config =self.sql_config
            io_config = self.sql_config
            self.init_shell = " /usr/local/mysql/bin/mysqldump -h{source_host} -P{source_port}  -u{source_user} -p{source_pwd}   --max_allowed_packet=64M  --net_buffer_length=4M " \
                              "--set-gtid-purged=OFF --single-transaction --databases dbname_position --tables tablename_postion  " \
                              "|/usr/local/mysql/bin/mysql -h{desc_host} -P{desc_port} -u{desc_user} -p{desc_pwd} {rewrite_db}".format(
                **self.config[0])


            self.dbname = " ".join(eval(self.config[0]["source_db"]))
            if self.config[0]["tables"]=='':
                self.tables = ''

                self.exec_shell = self.init_shell.replace("dbname_position", self.dbname).replace(" tablename_postion",
                                                                                              self.tables)
            else:
                self.tables = " ".join(eval(self.config[0]["tables"]))
                self.exec_shell = self.init_shell.replace("dbname_position", self.dbname).replace("tablename_postion",
                                                                                                  self.tables)

            self.result = ''
            print(self.exec_shell)
            # time.sleep(100)
            self.result = subprocess.Popen(self.exec_shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            retval=self.result.wait()

            self.stderr= self.result.stderr.readlines()

            print('########', self.result.stderr.readlines(),len(self.result.stderr.readlines()), '##')
            if len(self.stderr)==2:
                self.config_sql = '''update etl_config set io_config="{0}" ,sql_config="{1}" , is_init_data=0 where etl_name="{2}" '''.format(
                    self.io_config, self.sql_config, self.etl_name)
                self.dba_pool = MysqlPool.Mysql("dba")
                self.dba_pool.update(self.config_sql)
                self.dba_pool.end()
                self.dba_pool.close()
                print("初始化完成")
            else:
                self.log.writeLog.error('{0}全量初始化出错{1}'.format(self.etl_name, self.stderr))
                #msgBody = DingtalkApi.MessageBody(title="", msg='{0}全量初始化出错 {1}'.format(self.etl_name, self.stderr))
                msgBody='{0}全量初始化出错 {1}'.format(self.etl_name, self.stderr)
                dingsender.send(msgBody)
                exit(1)


if __name__ == '__main__':
    global sql_config
    global io_config
    global exit_thread
    global Q
    syncMysql = SyncMysql()
    syncMysql.check_process(syncMysql.etl_name)
    syncMysql.init_data()

    exit_thread = 0
    if syncMysql.config[0]["is_init_data"] == 0 :
        sql_config = syncMysql.config[0]["sql_config"]
        io_config = syncMysql.config[0]["io_config"]
    if syncMysql.config[0]["run_io_thread"] == 1 :
        t1 = threading.Thread(target=syncMysql.Io_thread)
        t1.setName('io_thread')
        t1.setDaemon(True)
        t1.start()
    #
    time.sleep(1)
    if syncMysql.config[0]["run_sql_thread"] == 1:
        t2 = threading.Thread(target=syncMysql.sql_thread)
        t2.setName("sql_thread")
        t2.setDaemon(True)
        t2.start()
    #

    t3 = threading.Thread(target=syncMysql.save_config)
    t3.setName("save_config")
    t3.setDaemon(True)
    t3.start()

    while 1:

        if  syncMysql.config[0]["run_io_thread"] == 1 :
            if not t1.is_alive()  :
                syncMysql.log.writeLog.error('  {0} 线程出错'.format(t1.getName()))
                #msgBody = DingtalkApi.MessageBody(title="",
                #                                 msg='  {0} 线程出错 etl_name:{1} '.format(t1.getName(), syncMysql.etl_name))
                msgBody='  {0} 线程出错 etl_name:{1} '.format(t1.getName(), syncMysql.etl_name)
                dingsender.send(msgBody)

                t1 = threading.Thread(target=syncMysql.Io_thread)
                t1.setName('io_thread')
                t1.setDaemon(True)
                t1.start()
        if  syncMysql.config[0]["run_sql_thread"] == 1 :
            if not t2.is_alive()   :
                syncMysql.log.writeLog.error('  {0} 线程出错'.format(t2.getName()))
                #msgBody = DingtalkApi.MessageBody(title="",
                #                                  msg='  {0} 线程出错 etl_name:{1}'.format(t2.getName(), syncMysql.etl_name))
                msgBody='  {0} 线程出错 etl_name:{1}'.format(t2.getName(), syncMysql.etl_name)
                dingsender.send(msgBody)
                # syncMysql.send_Mail(syncMysql.receiver, '  {0} 线程出错,etl_name:{1}'.format(t2.getName(),syncMysql.etl_name), '  {0}线程出错 etl_name:{1} '.format(t1.getName(),syncMysql.etl_name), '')
                t2 = threading.Thread(target=syncMysql.sql_thread)
                t2.setName("sql_thread")
                t2.setDaemon(True)
                t2.start()

        if not t3.is_alive():
            syncMysql.log.writeLog.error('  {0} 线程出错 etl_name:{1} '.format(t3.getName(), syncMysql.etl_name))
            #msgBody = DingtalkApi.MessageBody(title="", msg='  {0} 线程出错'.format(t3.getName()))
            msgBody='  {0} 线程出错'.format(t3.getName())
            dingsender.send(msgBody)
            # syncMysql.send_Mail(syncMysql.receiver, '  {0} 线程出错 etl_name:{1} '.format(t3.getName(),syncMysql.etl_name), '  {0}线程出错  etl_name:{1}'.format(t1.getName() ,syncMysql .etl_name), '')
            t3 = threading.Thread(target=syncMysql.save_config)
            t3.setName("save_config")
            t3.setDaemon(True)
            t3.start()

        if exit_thread == 1:
            exit(0)

        # print(io_config,sql_config)
        time.sleep(60)
