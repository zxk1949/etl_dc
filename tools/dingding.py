import requests
import json
import sys



class dingding:
    def __init__(self):
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token=82a32fbfe0e20a938cd34dca02f7fcf0422e65f7378412425d70163b96e3db67'
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
    def send_msg(self, text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": "notice:{0}".format(text)
            },
            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content

if __name__ == '__main__':
    ding = dingding()
    ding.send_msg(sys.argv)
