#!/usr/bin/python
#coding: utf-8  
import sys,os
import smtplib  

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SendMail:
    def __init__(self):
          
        self.sender = 'menglingyin@huohua.cn'
        self.smtpserver = 'smtp.exmail.qq.com'  
        self.username = 'menglingyin@huohua.cn'
        self.password = '9f.com.cn@QAZ'
        #创建一个带附件的实例
        self.msg = MIMEMultipart()		
    def Send(self,receiver,subject,MailBody,attachment=''):

        self.receiver=receiver
        body=MIMEText(MailBody,_charset="utf-8")
        self.msg.attach(body)
        #构造附件1
        if attachment!='':
            att1 = MIMEText(open(attachment, 'rb').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            att1["Content-Disposition"] = 'attachment; filename=%s'%(attachment)
            self.msg.attach(att1)
        #设置主题
        self.msg['Subject'] = Header(subject, 'utf-8')
        self.msg['to']=''
        self.msg['to'] = ";".join(self.receiver)
        self.msg['from'] = self.sender
        smtp = smtplib.SMTP_SSL(host=self.smtpserver)
        smtp.connect('smtp.exmail.qq.com',465)
        smtp.login(self.username, self.password)

        smtp.sendmail(self.msg['from'], self.receiver, self.msg.as_string())
        smtp.quit()
        smtp.close()

if __name__ == '__main__':
    sendMail=SendMail()
    receiver=[ "290634612@qq.com"]
    sendMail.Send(receiver,'测试测试','李晓蒙内容测试','/data0/python/huohua_db/tools/bigkey.txt')




  



