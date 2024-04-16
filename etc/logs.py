#!/usr/bin/python
#coding=utf-8
import logging
import sys

sys.path.append('.')
from etc import SendMail
class Log:
    def __init__(self):
        self.formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        self.writeLog = logging.getLogger('logs')
        self.writeLog.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler('../log/logs.log',encoding="utf-8")
        #self.fh = logging.FileHandler('/data0/python/log/logs.log')
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.formatter)
        self.writeLog.addHandler(self.fh)


if __name__ == '__main__':
    log=Log()
    log.writeLog.error('error test')
    log.writeLog.error('error test1')