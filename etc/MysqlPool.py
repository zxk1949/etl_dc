# -*- coding: UTF-8 -*-
"""
desc:数据库操作类
@note:
1、执行带参数的ＳＱＬ时，请先用sql语句指定需要输入的条件列表，然后再用tuple/list进行条件批配
２、在格式ＳＱＬ中不需要使用引号指定数据类型，系统会根据输入参数自动识别
３、在输入的值中不需要使用转意函数，系统会自动处理
"""

import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from etc import config as Config

"""
Config是一些数据库的配置文件
"""

class Mysql(object):
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
        获取连接对象：conn = Mysql.getConn()
        释放连接对象;conn.close()或del conn
    """
    #连接池对象
    __pool = None
    def __init__(self,dbname):
        """
        数据库构造函数，从连接池中取出连接，并生成操作游标
        """
#        self._conn = pymysql.connect(host=Config.DBHOST , port=Config.DBPORT , user=Config.DBUSER , passwd=Config.DBPWD ,
#                              db=Config.DBNAME, charset=Config.DBCHAR,cursorclass=DictCursor)
        self._conn = Mysql.__getConn(dbname)

        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn(dbname):
        """
        @summary: 静态方法，从连接池中取出连接
        @return pymysql.connection
        """
        if Mysql.__pool is None:


           if dbname == 'groot_data_center':
               __pool = PooledDB(creator=pymysql, mincached=5, maxcached=30,
                              host=Config.db_host70, port=Config.db_port70, user=Config.db_user70,
                              passwd=Config.db_password70,
                              db=Config.db_name70, charset='utf8mb4', cursorclass=DictCursor, autocommit=1)
               return __pool.connection()


           if dbname == 'qa_test_emp':
                __pool = PooledDB(creator=pymysql, mincached=5, maxcached=30,
                              host=Config.db_host71, port=Config.db_port71, user=Config.db_user71,
                              passwd=Config.db_password71,
                              db=Config.db_name71, charset='utf8mb4', cursorclass=DictCursor, autocommit=1)
                return __pool.connection()

    def getAll(self,sql,param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchall()


        else:
            result = False

        return result


    def getMany(self,sql,num,param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertOne(self,sql ):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """

        self._cursor.execute(sql )
        return self.__getInsertId()

    def insertMany(self,sql,values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql,values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self,sql,param=None):
        if param is None:

                count = self._cursor.execute(sql)


        else:

                count = self._cursor.execute(sql,param)

        return count

    def update(self,sql,param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def delete(self,sql,param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.begin()

    def end(self,option='commit'):
        """
        @summary: 结束事务
        """
        if option=='commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def close(self):
        """
        @summary: 释放连接池资源
        """
        self._cursor.close()
        self._conn.close()
