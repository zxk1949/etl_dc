# encoding=utf-8

import datetime
import time
class DateTool():
    def __init__(self):
        pass
    def datetime_toString(self,dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    #把字符串转成datetime
    def string_toDatetime(self,string):
        return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    #把字符串转成datet
    def stringDateTime_toDatet(self,string):
        time1= datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return time1.strftime("%Y-%m-%d")

    #把字符串转成时间戳形式
    def string_toTimestamp(self,strTime):
        return time.mktime(DateTool.string_toDatetime(strTime).timetuple())

    #把时间戳转成字符串形式
    def timestamp_toString(self,stamp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stamp))

    #把datetime类型转外时间戳形式
    def datetime_toTimestamp(self,dateTim):
        return time.mktime(dateTim.timetuple())
    #字符串日期加减，并返回字符串日期
    def addDatetime(self,strTime,day):
        time=datetime.datetime.strptime(strTime,"%Y-%m-%d")
        time2=time+datetime.timedelta(days=day)
        return time2.strftime("%Y-%m-%d")

    def diffDays(self,date1,date2):
        #%Y-%m-%d为日期格式，其中的-可以用其他代替或者不写，但是要统一，同理后面的时分秒也一样；可以只计算日期，不计算时间。
        #date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
        #date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
        date1=time.strptime(date1,"%Y-%m-%d")
        date2=time.strptime(date2,"%Y-%m-%d")
        date1=datetime.datetime(date1[0],date1[1],date1[2])
        date2=datetime.datetime(date2[0],date2[1],date2[2])
        #返回两个变量相差的值，就是相差天数

        return  (date1-date2).days
if __name__ == '__main__':
    dateTool=DateTool()
    print (dateTool.stringDateTime_toDatet('2018-01-03 8:00:09' ))