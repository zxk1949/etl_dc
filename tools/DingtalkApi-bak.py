# encoding=utf-8
# 李晓蒙
"""
推送钉钉消息到群组工具
"""
import json
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
import json

class MessageBody(object):
    """ 推送消息内容体
    """

    def __init__(self, title="", msg=""):
        """初始化一个消息体

        Keyword Arguments:
            title {str} -- 消息标题 (default: {""})
            msg {str} -- 消息体 (default: {""})
        """
        super().__init__()
        self._msg = title
        self._title = msg

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, msg: str):
        self._msg = msg

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    def getDingMessage(self, at, isAtAll):
        return json.dumps({

            "msgtype": "text",
            "text": {
                "content": "Notice："+self.title + "\n" + self.msg
            },
            "at": {
                "atMobiles": at,
                "isAtAll": isAtAll
            }
        })


class Sender():
    """消息推送器
    """

    def __init__(self):
        """初始化一个消息推送器

        Arguments:
            webhook {[type]} -- 机器人webHook
        """
        super().__init__()
        #self.url = "https://oapi.dingtalk.com/robot/send?access_token=0371dfc10ccbf3458e3156ee704b36a4d5983bf5774b3918c50ca5385ed05d35"
        self.usrl="https://open.feishu.cn/open-apis/bot/v2/hook/dc3ef7c0-fc17-45ce-a2f7-c5b625df604a"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.msgType = "text"

    def send(self, msgBody: MessageBody, at=[], isAtAll=False):
        """推送消息

        Arguments:
            msgBody {MessageBody} -- 推送消息对象

        Keyword Arguments:
            at {list} -- 指定@的人 (default: {[]})
            isAtAll {bool} -- 是否@所有人 (default: {False})
        """
        str_timestamp = str(round(time.time() * 1000))
        #secret = 'SECae3fdb61309b6f3107dabc328b9cec51f83333fc234d69f1894f23f302445e76'
        secret='jCIx7vPm0dIT0TcoFIShng'
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(str_timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        str_sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        self.url=self.url+"&timestamp={0}&sign={1}".format(str_timestamp,str_sign)
        msg = msgBody.getDingMessage(at, isAtAll)
        result=requests.post(headers=self.headers, data=msg, url=self.url)
        # print(result.content)
class SendTOSA():
    """消息推送器
    """

    def __init__(self):
        """初始化一个消息推送器

        Arguments:
            webhook {[type]} -- 机器人webHook
        """
        super().__init__()
        self.url = "https://oapi.dingtalk.com/robot/send?access_token=afbb071567acef01ada26665fc5345bc1856b24f445fd9c1b90acb1e7e368fc7"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.msgType = "text"

    def sendToSa(self, msgBody: MessageBody, at=[], isAtAll=False):
        """推送消息

        Arguments:
            msgBody {MessageBody} -- 推送消息对象

        Keyword Arguments:
            at {list} -- 指定@的人 (default: {[]})
            isAtAll {bool} -- 是否@所有人 (default: {False})
        """
        str_timestamp = str(round(time.time() * 1000))
        secret = 'SEC21ce004863c8ae724aa248151335c616fadbf40e480438a956fb8d436c8c76b5'
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(str_timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        str_sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        self.url=self.url+"&timestamp={0}&sign={1}".format(str_timestamp,str_sign)
        msg = msgBody.getDingMessage(at, isAtAll)
        result=requests.post(headers=self.headers, data=msg, url=self.url)
        # print(result.content)
# if __name__ == '__main__':
#
#     msgBody = MessageBody(title="", msg="world22222222222222222")
#     sender = Sender()
#     sender.send(msgBody)(base)
