#!/usr/bin/env python3
# coding: utf-8
import os
import xlwt
import pymysql
import datetime
import sys
sys.path.append("..")
from etc import SendMail
import time

class MysqlToExcel(object):
    def __init__(self):
        self.host = '10.89.90.56'
        self.user = 'root'
        self.passwd = 'Dba@2019huohua!'
        self.db_name = 'push_service'
        self.port = 3306
        self.file_name = 'data.xls'

    def get_query_results(self):
        sql = '''SELECT
		( CASE channel WHEN 'HUOHUA_PRD' THEN '火花生产' WHEN 'HUOHUA_MKT' THEN '火花营销' 
									 WHEN 'HUOHUA_AI_PRD' THEN '火花AI课生产' WHEN 'HUOHUA_AI_MKT' THEN '火花AI课营销' 
									 WHEN 'HUOHUA_BC_PRD' THEN '火花编程生产' WHEN 'HUOHUA_BC_MKT' THEN '火花编程营销' 
									 ELSE '未知' END ) '短信通道',
		type_name `Key`,
		msg '内容',
		(
			CASE gateway_type 
				WHEN 0 THEN
					'梦网' 
				WHEN 1 THEN
					'助通' 
				WHEN 2 THEN
					'维托安' 
				WHEN 3 THEN
					'联动世纪' 
				WHEN 4 THEN
					'国际梦网' 
				WHEN 5 THEN
					'麦盟' 
				WHEN 6 THEN
					'腾讯云'
				WHEN 7 THEN
					'国都国内'
				WHEN 8 THEN
					'国都国际'
				ELSE 
					'未知' 
			END 
		) '短信服务商',
		count( DISTINCT phone ) '手机号数',
		sum( sp_cnt ) '计费条数',
		count( 1 ) '发送次数' 
	FROM 
		sms 
	WHERE
		create_time BETWEEN date_format(date_sub(CURDATE(), interval 1 month),'%Y-%m-01 00:00:00') 
		AND date_format(CURDATE(),'%Y-%m-01 00:00:00') 
		AND type_name <> 'smc.huohua.mkt' 
	GROUP BY
		channel,
		gateway_type,
		type_name 

UNION ALL
(
	SELECT
		'火花营销' '短信通道',
		type_name `Key`,
		msg '内容',
		(
		CASE gateway_type 
			WHEN 0 THEN
				'梦网' 
			WHEN 1 THEN
				'助通' 
			WHEN 2 THEN
				'维托安' 
			WHEN 3 THEN
				'联动世纪' 
			WHEN 4 THEN
				'国际梦网' 
			WHEN 5 THEN
				'麦盟' 
			WHEN 6 THEN
				'腾讯云' 
			WHEN 7 THEN
				'国都国内'
			WHEN 8 THEN
				'国都国际'
			ELSE 
				'未知' 
			END 
			) '短信服务商',
			count( DISTINCT phone ) '手机号数',
			sum( sp_cnt ) '计费条数',
			count( 1 ) '发送次数' 
		FROM
			sms 
		WHERE
			create_time BETWEEN date_format(date_sub(CURDATE(), interval 1 month),'%Y-%m-01 00:00:00') 
			AND date_format(CURDATE(),'%Y-%m-01 00:00:00') 
			AND type_name = 'smc.huohua.mkt' 
		GROUP BY
			gateway_type,
			request_sn 
)'''

        conn = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            port=self.port,
            database=self.db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        cur = conn.cursor()  # 创建游标
        cur.execute(sql)  # 执行sql命令
        result = cur.fetchall()  # 获取执行的返回结果
        # print(result)
        cur.close()
        conn.close()  # 关闭mysql 连接
        return result

    def generate_table(self):
        """
        生成excel表格
        :return:
        """
        # 删除已存在的文件
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

        result = self.get_query_results()
        # print(result)
        if not result:
            print("查询结果为空")
            return False

        # 创建excel对象
        f = xlwt.Workbook()
        sheet1 = f.add_sheet('Sheet1', cell_overwrite_ok=True)

        # 第一行结果
        row0 = result[0]
        # 列字段
        column_names = list(row0)

        # 写第一行，也就是列所在的行
        for i in range(0, len(row0)):
            sheet1.write(0, i, column_names[i])

        # 写入多行
        # 行坐标，从第2行开始，也是1
        for row_id in range(1, len(result) + 1):
            # 列坐标
            for col_id in range(len(column_names)):
                # 写入的值
                value = result[row_id - 1][column_names[col_id]]
                # 判断为日期时
                if isinstance(value, datetime.datetime):
                    value = result[row_id - 1][column_names[col_id]].strftime('%Y-%m-%d %H:%M:%S')

                # 写入表格
                sheet1.write(row_id, col_id, value)

        # 保存文件
        f.save(self.file_name)

        # 判断文件是否存在
        if not os.path.exists(self.file_name):
            print("生成excel失败")
            return False

        print("生成excel成功")
        return True

if __name__ == '__main__':
    MysqlToExcel().generate_table()
    mail1 = SendMail.SendMail()
    receiver = ['wangzizhao@huohua.cn', 'duanzexun@huohua.cn','haoyongjian@huohua.cn']
    mail1.Send(receiver, '短信发送记录月度统计', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , 'data.xls')
    os.remove('data.xls')


