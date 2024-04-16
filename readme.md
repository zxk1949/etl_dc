###
mysql 同步工具
###
 ####
_1. 依赖环境_
 ####
python 3.8 以上版本  
pip install -r requirements.txt  
本工具的目的在于轻量化部署mysql 同步，同时兼顾数据一致性，以及数据完整性，解决同步时使用pt 工具进行ddl操作时的一些痛点。
####
_2. 功能介绍_
####
本工具的功能主要有：

全量+增量同步：同步源数据库的全部数据和新增数据到目标数据库;  
数据一致性：本工具通过对比源数据库和目标数据库的表结构和数据，保证数据一致性;  
数据完整性：本工具通过对比源数据库和目标数据库的表结构和数据，保证数据完整性，并提供修复数据的功能;  
数据库分表时可作为实时同步工具，实时同步源数据库的新增数据到目标数据库             

####
 _3. 使用说明_
####
 初始化表结构和数据  
 【说明：修改engine 再初始化表结构和数据】    
 python models.py  
 配置congfig.py信息（目标端），MysqlPool.py 目标端的连接信息,如图:  

 ![1712912914157.jpg](image%2F1712912914157.jpg)  
 ![1712912942522.jpg](image%2F1712912942522.jpg)

 etl_config表中配置源数据库和目标数据库的连接信息，以及需要同步的表名,如图：  

 ![1712913265811.jpg](image%2F1712913265811.jpg)
 
启动同步：  
 nohub python Etlt.py etl_name &  
添加监控项：
在表watch_process 中添加  
告警通知：  
tool/DingtalkApi.py
 
 
    