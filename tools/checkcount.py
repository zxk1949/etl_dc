# encoding=utf-8
import os
import sys
sys.path.append('.')
sys.path.append('../')
from etc import MysqlPool
import time

table_list = ['black_box_configuration','quality_inspection_appeal','quality_inspection_sheet','business_attachment','call_data_record','contacts','crm_operate_log','cust_activity','cust_channel_label','cust_operate_log','cust_roated_record','customer','customer_agent','customer_ai','customer_black_box','customer_black_box_performance','customer_experience_course','customer_extension','customer_history','customer_not_transform_reason','customer_not_transform_reason_item','customer_order','customer_order_agent','customer_order_item','customer_overseas','customer_protect_history','customer_send_log','customer_sms_record','customer_statistics_detail','customer_statistics_setting','customer_student_tag_log','customer_tag','customer_trace_0','customer_trace_1','customer_trace_2','customer_trace_3','customer_trace_4','customer_trace_5','customer_trace_6','customer_trace_7','customer_trace_8','customer_trace_9','customer_weixin','delivery_order','delivery_order_item','employee_profile','oversea_allocate_record','oversea_to_sale_schedule','quality_inspection_log','sale_invite','sale_setting_month_target','sale_statistics_daily','sale_statistics_daily_call','sale_target_completion_rate','sales_employee','sales_schedule','simple_agent','simple_user','student_learn_information','student_tag','user_agent','user_relation_detail','user_relation_statistics']
mysqlPool = MysqlPool.Mysql('datacenter')
time1 = time.strftime("%Y-%m-%d", time.localtime())
for t1 in table_list:
    count1 = mysqlPool.getAll('select count(*) from %s' %t1)
    with open('count1_'+time1+'.txt', "a", encoding='utf-8') as fw:
        fw.write("table:%s,%s \n" %(t1,count1))
