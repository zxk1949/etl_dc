#!/bin/env python3.6
# encoding=utf-8
# auth: wzz


import pymysql
import time

'''
transport data  from one mysql db  to  anathor mysql db
'''

if __name__ == "__main__":

    sourdbhost = '10.89.89.61'
    sourcedb = 'peppa'
    sourtable = 'lesson_report_classroom_behave'
    step = 0.1

    targethost = '10.89.87.15'
    targetdb = 'learning_situation'
    targettable = 'lesson_report_classroom_behave'

    tablemaxid = 12427117
    id = 1

    sourcedb1 = pymysql.connect(sourdbhost, 'root', 'Dba@2019huohua!', sourcedb, charset='utf8')
    sourcecursor1 = sourcedb1.cursor()
    targetdb1 = pymysql.connect(targethost, 'root', 'Dba@2019huohua!', targetdb, charset='utf8')
    targetcursor1 = targetdb1.cursor()

    insertsql = "insert into lesson_report_classroom_behave(id,lesson_report_id,user_id,student_id,lesson_id,classroom_id,stage_reward_num,stage_durian,single_stage_nun,open_wheat_duration,courseware_stage_num,responder_num,shake_num,teacher_reward_num,game_complete_reward_num,avg_interact_time,avg_interact_class_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    oplog = open('lesson_report_classroom_behave_insert.log', 'a')

    while id <= tablemaxid:
        sql1 = "select * from " + str(sourtable) + " where id >= " + str(id) + " and id < " + str(id) + " +1000"
        try:
            sourcecursor1.execute(sql1)
            data = sourcecursor1.fetchall()
            targetcursor1.executemany(insertsql, data)
            targetdb1.commit()
        except Exception as e:
            print(e)

        id += 1000
        oplog.write(str(id) + " copy done\n")
        time.sleep(step)

    sourcedb1.close()
    targetdb1.close()
    oplog.close()
