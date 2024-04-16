# This file is used to create the table structure of the database.
# The table structure is defined by the ORM base class Base and the table classes ETLConfig and WatchProcess.
# The database engine is created using the create_engine function.
# author: zxk

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.sql import func

from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 创建ORM基类
Base = declarative_base()
# 创建MySQL数据库引擎
#engine = create_engine('mysql+mysqlconnector://root:root@10.208.0.118:33066/dba_test', echo=True)
# 如果使用PyMySQL，则替换连接字符串为：
engine = create_engine('mysql+pymysql://root:root@10.208.0.118:33066/dba_test', echo=True)

class ETLConfig(Base):
    __tablename__ = 'etl_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    etl_name = Column(String(100), nullable=False, unique=True)
    io_config = Column(String(500))
    sql_config = Column(String(500))
    create_time = Column(DateTime, default=func.now())
    uptime_time = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    source_db = Column(String(100))
    rewrite_db = Column(String(100))
    tables = Column(String(4000))
    source_host = Column(String(100))
    source_port = Column(Integer)
    source_user = Column(String(100))
    source_pwd = Column(String(100))
    desc_dbpool = Column(String(100), comment='日志应用的目的连接池名称')
    is_init_data = Column(Integer, default=0, comment='是否初始化')
    desc_host = Column(String(100), comment='初始化时目的主机')
    desc_port = Column(Integer, comment='初始化时目的主机端口')
    desc_user = Column(String(100), comment='初始化时目的用户')
    desc_pwd = Column(String(100), comment='初始化时目的密码')
    relay_log_dir = Column(String(100), comment='完整relay log 目录，如/data0/log/')
    run_io_thread = Column(Integer, default=1, comment='是否运行io线程  1 运行  0 不运行')
    run_sql_thread = Column(Integer, default=1, comment='是否运行sql 线程 1 运行  0 不运行')

class WatchProcess(Base):

    __tablename__ = 'watch_process'

    id=Column(Integer, primary_key=True, autoincrement=True)
    process_name=Column(String(100), nullable=False, unique=True)
    run_command=Column(String(500), nullable=False)
    is_del=Column(Integer, default=0, comment='0 阿里云，1 停监控 2 腾讯云 (89.66),4 (118),5(废弃), 6 (asc 硅谷 64.195 )',)
    create_time=Column(DateTime, default=func.now())
    uptime_time=Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    remark=Column(String(500), comment='备注')
    auto_run=Column(Integer, default=0)



# 创建表结构
Base.metadata.create_all(engine)
# 创建数据库会话
Session = sessionmaker(bind=engine)
session = Session()
# 初始化数据
etl_config_data = {
    'etl_name': 'qa_test_emp',
    'io_config': "{'log_file':'mysql-bin.000287','log_pos':284312383}",
    'sql_config': "{'log_pointer':4356,'log_file':'mysql-bin.000287','log_pos':283358419}",
    'create_time': datetime(2024, 4, 11, 14, 12, 0),
    'uptime_time': datetime(2024, 4, 11, 20, 7, 50),
    'source_db': 'se_emp',
    'rewrite_db': '',
    'tables': '[\'emp\']',
    'source_host': '10.208.0.118',
    'source_port': 33066,
    'source_user': 'root',
    'source_pwd': 'root',
    'desc_dbpool': 'qa_test_emp',
    'is_init_data': 0,
    'desc_host': '10.208.0.118',
    'desc_port': 33066,
    'desc_user': 'root',
    'desc_pwd': 'root',
    'relay_log_dir': '/data0/python/huohua_db/etl_dc/qa_118_emp/',
    'run_io_thread': 1,
    'run_sql_thread': 1
}
watch_process_data = {
    'process_name': 'qc_teach_quality_to_dc',
    'run_command': 'cd /data0/python/huohua_db/etl_dc/ ; nohup /usr/local/anaconda3/bin/python /data0/python/huohua_db/etl_dc/Etl_DC.py qc_teach_quality_to_dc &',
    'is_del': 2,
    'create_time': datetime(2024, 4, 11, 14, 12, 0),
    'uptime_time': datetime(2024, 4, 11, 20, 7, 50),
    'remark': '测试用例',
    'auto_run': 1
}
# 创建ETLConfig对象
etl_config = ETLConfig(**etl_config_data)
watch_process = WatchProcess(**watch_process_data)
# 将对象添加到会话
session.add(etl_config)
session.add(watch_process)
# 提交会话，将数据保存到数据库
session.commit()
# 关闭会话
session.close()