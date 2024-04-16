# encoding=utf-8
#!/usr/bin/python

import os
import sys
import datetime,time

def init_db_info():
    url='mysql+pymysql://root:root@10.208.0.118:33066/dba_test'
    return url

#impush
db_host1='10.89.90.14'
db_port1=3306
db_user1='root'
db_password1='Dba@2019huohua!'
db_name1="spush_stats_db"



#db审核平台库
db_host2='10.89.87.83'
db_port2=3306
db_user2='root'
db_password2='Dba@2019huohua!'
db_name2='db_monitor'



#dev
db_host3='10.253.188.157'
db_port3=3306
db_user3='root'
db_password3='Vso0ViKRU='


#dev
db_host3='rm-2ze7u6nfkxwxhs76133150.mysql.rds.aliyuncs.com'
db_port3=3306
db_user3='root'
db_password3='Vso0ViKRU='


#sim同步
db_host4='10.250.100.91'
db_port4=3306
db_user4='root'
db_password4='6jRLTpKD5P'
db_name4='mysql'



#sim主库126
db_host5='10.32.0.197'
db_port5=3306
db_user5='root'
db_password5='6jRLTpKD5P'
db_name5='mysql'



#sim主库peppa
db_host7='10.250.100.92'
db_port7=3306
db_user7='root'
db_password7='6jRLTpKD5P'
db_name7='peppa'

#仓库
db_host6='10.89.87.19'
db_port6=3306
db_user6='root'
db_password6='Dba@2019huohua!'
db_name6='operation'

#主库peppa
db_host8='10.89.89.61'
db_port8=3306
db_user8='root'
db_password8='Dba@2019huohua!'
db_name8='peppa'

#xxl-job
db_host9='10.89.90.68'
db_port9=3306
db_user9='root'
db_password9='Dba@2019huohua!'
db_name9='xxl-job'


#crm
db_host10='10.89.87.3'
db_port10=3306
db_user10='root'
db_password10='Dba@2019huohua!'
db_name10='crm'


#sim主库crm
db_host11='10.250.100.92'
db_port11=3306
db_user11='root'
db_password11='6jRLTpKD5P'
db_name11='crm'

#crm
db_host12='10.89.90.142'
db_port12=3306
db_user12='root'
db_password12='Dba@2019huohua!'
db_name12='payment'

#stueent
db_host13='10.89.87.64'
db_port13=3306
db_user13='root'
db_password13='Dba@2019huohua!'
db_name13='student_reward'


#sms

db_host13='10.89.90.140'
db_port13=3306
db_user13='root'
db_password13='Dba@2019huohua!'
db_name13='push_service'


#opengalaxy

db_host14='10.89.87.46'
db_port14=3306
db_user14='root'
db_password14='Dba@2019huohua!'
db_name14='opengalaxy'

#腾讯 to sim主库
db_host15='10.32.10.105'
db_port15=3306
db_user15='root'
db_password15='6jRLTpKD5P'
db_name15='mysql'

#qa
db_host16='rm-2zet730iz01f1tvr2.mysql.rds.aliyuncs.com'
db_port16=3306
db_user16='qa_root'
db_password16='Vso0ViKRU='
db_name16='mysql'

#misc
db_host17='10.89.87.92'
db_port17=3306
db_user17='root'
db_password17='Dba@2019huohua!'
db_name17='misc'


#practice
db_host18='10.89.90.64'
db_port18=3306
db_user18='root'
db_password18='Dba@2019huohua!'
db_name18='practice'


#practice_recommend
db_host19='10.89.90.64'
db_port19=3306
db_user19='root'
db_password19='Dba@2019huohua!'
db_name19='practice_recommend'


#dba tx
db_host20='10.89.87.83'
db_port20=3306
db_user20='root'
db_password20='Dba@2019huohua!'
db_name20='dba'


# asset
db_host21='10.89.87.19'
db_port21=3306
db_user21='root'
db_password21='Dba@2019huohua!'
db_name21='asset'

# datacenter
db_host22='10.89.90.208'
db_port22=3306
db_user22='root'
db_password22='Dba@2019huohua!'
db_name22='mysql'


# classes slave
db_host23='10.89.90.47'
db_port23=3306
db_user23='root'
db_password23='Dba@2019huohua!'
db_name23='classes'


# crmthirdparty
db_host24='10.89.87.7'
db_port24=3306
db_user24='root'
db_password24='Dba@2019huohua!'
db_name24='crmthirdparty'



# cc
db_host25='10.89.87.116'
db_port25=3306
db_user25='root'
db_password25='Dba@2019huohua!'
db_name25='cc'

# immanager
db_host26='10.89.89.221'
db_port26=3306
db_user26='root'
db_password26='Dba@2019huohua!'
db_name26='immanager'

# shard immanager
db_host27='10.89.95.85'
db_port27=3406
db_user27='imma_rw'
db_password27='VyY4a03^rye3pxUI'
db_name27='immanager'

# shard sim
db_host28='10.250.100.91'
db_port28=3308
db_user28='sim_user'
db_password28='sim_user'
db_name28='immanager'


# la_ai
db_host29='10.89.87.61'
db_port29=3306
db_user29='root'
db_password29='Dba@2019huohua!'
db_name29='la_ai'

# dc
db_host30='10.89.87.81'
db_port30=3306
db_user30='root'
db_password30='Dba@2019huohua!'
db_name30='ucenter_sync'


#sim主库127
db_host31='10.89.87.81'
db_port31=3306
db_user31='root'
db_password31='Dba@2019huohua!'
db_name31='teach_evaluate_sync'

#sim主库128
db_host32='10.32.0.225'
db_port32=3306
db_user32='root'
db_password32='6jRLTpKD5P'
db_name32='mysql'

#sim主库128
db_host32='10.32.0.225'
db_port32=3306
db_user32='root'
db_password32='6jRLTpKD5P'
db_name32='mysql'

# order
db_host33='10.89.87.101'
db_port33=3306
db_user33='root'
db_password33='Dba@2019huohua!'
db_name33='order_center'


# sa_xxljob
db_host34='10.89.89.39'
db_port34=3306
db_user34='root'
db_password34='Dba@2019huohua!'
db_name34='xxl_job'


# datacenter_crmthirdparty
db_host35='10.89.90.208'
db_port35=3306
db_user35='root'
db_password35='Dba@2019huohua!'
db_name35='crmthirdparty'


# ai_learning_plan
db_host36='10.89.87.99'
db_port36=3306
db_user36='root'
db_password36='Dba@2019huohua!'
db_name36='ai_learning_plan'

# audition_report
db_host37='10.89.87.249'
db_port37=3306
db_user37='root'
db_password37='Dba@2019huohua!'
db_name37='audition_report'



#ticket
db_host38='10.89.87.124'
db_port38=3306
db_user38='root'
db_password38='Dba@2019huohua!'
db_name38='ticket'



#classroom
db_host39='10.89.87.222'
db_port39=3306
db_user39='root'
db_password39='Dba@2019huohua!'
db_name39='mock_classroom'


#la_sop
db_host40='10.89.87.97'
db_port40=3306
db_user40='root'
db_password40='Dba@2019huohua!'
db_name40='la_sop'


#student_reward_sharding
db_host41='10.89.89.66'
db_port41=3310
db_user41='root'
db_password41='root'
db_name41='student_reward'

#ai_learning_plan_sharding
db_host42='10.89.87.192'
db_port42=3310
db_user42='root'
db_password42='root'
db_name42='ai_learning_plan_sharding'


#datacenter2
db_host43='10.89.87.192'
db_port43=3306
db_user43='root'
db_password43='Dba@2019huohua!'
db_name43='mysql'


#asset_point
db_host44='10.89.87.217'
db_port44=3306
db_user44='root'
db_password44='Dba@2019huohua!'
db_name44='asset_point'


#antauge
db_host45='10.89.87.39'
db_port45=3306
db_user45='root'
db_password45='Dba@2019huohua!'
db_name45='antauge'


#antauge_sharding
db_host46='10.89.89.66'
db_port46=3313
db_user46='root'
db_password46='rootroot'
db_name46='antauge'

#practice
db_host47='10.89.89.66'
db_port47=3314
db_user47='root'
db_password47='rootroot'
db_name47='practice'


#teach_teacher
db_host48='10.89.87.244'
db_port48=3306
db_user48='root'
db_password48='Dba@2019huohua!'
db_name48='teach_teacher'


# dc_teach_teacher_sync
db_host49='10.89.87.81'
db_port49=3306
db_user49='root'
db_password49='Dba@2019huohua!'
db_name49='teach_teacher_sync'


#practice_qa_log
db_host50='10.250.100.91'
db_port50=3320
db_user50='root'
db_password50='root'
db_name50='practice'


#classes_sharding
db_host51='10.89.89.66'
db_port51=3320
db_user51='root'
db_password51='rootroot'
db_name51='classes_sharding'


#question_sharding
db_host52='10.89.89.66'
db_port52=3322
db_user52='root'
db_password52='rootroot'
db_name52='question_sharding'


#classes
db_host53='10.89.89.66'
db_port53=3323
db_user53='root'
db_password53='rootroot'
db_name53='classes'


#
db_host54='se-mysql-sim.cirplnnl2h9c.ap-southeast-1.rds.amazonaws.com'
db_port54=3306
db_user54='root'
db_password54='6jRLTpKD5P'
db_name54='se_peppa_account'


#
db_host55='se-mysql-sim.cirplnnl2h9c.ap-southeast-1.rds.amazonaws.com'
db_port55=3306
db_user55='root'
db_password55='6jRLTpKD5P'
db_name55='se_emp'

db_host56='prod-my-se-operation.cirplnnl2h9c.ap-southeast-1.rds.amazonaws.com'
db_port56=3306
db_user56='root'
db_password56='Dba2019huohua!'
db_name56='se_peppa_account'

db_host57='prod-my-se-operation.cirplnnl2h9c.ap-southeast-1.rds.amazonaws.com'
db_port57=3306
db_user57='root'
db_password57='Dba2019huohua!'
db_name57='se_emp'


#emp_test
db_host58='10.208.0.118'
db_port58=33066
db_user58='root'
db_password58='root'
db_name58='se_emp'


#qc_emp_to_se_emp_sim_tencent_email_mapping-part_time_employee
db_host59='se-mysql-sim.cirplnnl2h9c.ap-southeast-1.rds.amazonaws.com'
db_port59=3306
db_user59='root'
db_password59='6jRLTpKD5P'
db_name59='se_emp'



#qc_emp_to_se_emp_online_tencent_email_mapping-part_time_employee
db_host60='prod-my-se-operation.cirplnnl2h9c.ap-southeast-1.rds.amazonaws.com'
db_port60=3306
db_user60='root'
db_password60='Dba2019huohua!'
db_name60='se_emp'



db_host61='10.101.32.12'
db_port61=3306
db_user61='root'
db_password61='Dba@2019huohua!'
db_name61='se_peppa_account'


db_host62='10.101.32.12'
db_port62=3306
db_user62='root'
db_password62='Dba@2019huohua!'
db_name62='se_emp'


db_host63='10.101.32.12'
db_port63=3306
db_user63='root'
db_password63='Dba@2019huohua!'
db_name63='se_sso'



db_host64='10.208.0.118'
db_port64=33066
db_user64='root'
db_password64='root'
db_name64='se_emp'


db_host65='10.101.32.12'
db_port65=3306
db_user65='root'
db_password65='Dba@2019huohua!'
db_name65='se_oa_portal'



#synuc_hulk_account_asc
db_host66='10.96.64.73'
db_port66=3306
db_user66='root'
db_password66='Dba@2019huohua!'
db_name66='hulk_account_asc'


#synuc_asc_oa_portal_online
db_host67='10.96.66.22'
db_port67=3306
db_user67='root'
db_password67='Dba@2019huohua!'
db_name67='asc_peppa_oa_portal'


#qa_emp_to_qa_hr_contract
db_host68='10.250.0.184'
db_port68=3306
db_user68='qa_root'
db_password68='Vso0ViKRU='
db_name68='hr_contract'


#online_emp_to_online_hr_contract
db_host69='10.89.87.174'
db_port69=3306
db_user69='root'
db_password69='Dba@2019huohua!'
db_name69='hr_contract'

# prod-my-hulk_class_help , groot_data_center
db_host70='10.96.64.226'
db_port70=3306
db_user70='root'
db_password70='Dba@2019huohua!'
db_name70='groot_data_center'

# qa_118
db_host71='10.208.0.118'
db_port71=33066
db_user71='root'
db_password71='root'
db_name71='se_emp'

