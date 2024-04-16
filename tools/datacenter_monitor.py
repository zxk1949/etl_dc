from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
import json
import pymysql
import requests



#连接池类

class Mysql(object):
    __pool = None
    def __init__(self):
        self._conn = pymysql.connect(host='10.89.90.208', port= 3306, user='root' , passwd='Dba@2019huohua!' ,database = 'mysql', charset='utf8mb4',cursorclass=DictCursor)
        self._conn = Mysql.__getConn()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return pymysql.connection
        """
        if Mysql.__pool is None:
            __pool = PooledDB(creator=pymysql, mincached=2 , maxcached=30 ,host='10.89.90.208' , port=3306 , user='root' , passwd='Dba@2019huohua!' , charset='utf8mb4',cursorclass=DictCursor,autocommit=1)
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
        self._conn.autocommit(0)

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

#dingding推送消息






class dingding:
    def __init__(self):
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token=82a32fbfe0e20a938cd34dca02f7fcf0422e65f7378412425d70163b96e3db67'
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
    def send_msg(self, text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": "notice:{0}".format(text)
            },
            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content






if __name__ == '__main__':
    ding = dingding()
    result = Mysql().getAll("show slave status")
    for i in result:
        if i['Slave_IO_Running'] != 'Yes' or i['Slave_SQL_Running'] != 'Yes':
                msg1 = "{0} 报错，错误信息:{1}".format(i['Channel_Name'],i['Last_Error'])
                ding.send_msg(msg1)

